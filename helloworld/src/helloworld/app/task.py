import asyncio
import uuid
from .log import logger
from .device import device_manager
from .db.utils import get_all_devices, trim_points_for_metric
from .db.models import Device


# async def pytest_job():
#     await asyncio.sleep(60)
#     logger.info("test_job")

# async def modbusRTU_job(device_id:str="all"):
#     logger.info(f"modbusRTU_job start, {device_id}")

#     tasks = []
#     for devid, dev in device_manager.devices.items():
#         print(devid)
#         task = asyncio.create_task(dev.sample())
#         tasks.append(task)
#     await asyncio.gather(*tasks)
#     # message = f"{{'id':'modbusRTU_job', 'temp':{random.randint(20, 30)}}}"
#     # topic = "sensor"
#     # # pub.sendMessage(topicName=topic, message=message)
#     # bus.publish(topic, message=message)
#     # print(f"[传感器] 发送数据到 {topic}: {message}")
#     # await asyncio.sleep(2)
#     logger.info("modbusRTU_job finished")

# async def modbusTCP_job():
#     logger.info("modbusTCP_job start")
#     await asyncio.sleep(1)
#     logger.info("modbusTCP_job finished")

async def sample_job(device_id:str):
    logger.info(f"sample start, {device_id}")
    if device_id == "all":
        tasks = [asyncio.create_task(device.sample()) for devid, device in device_manager._devices.items()]
        await asyncio.gather(*tasks)
    else:
        # for devid, device in device_manager._devices.items():
        #     print("devid=", devid, device)
        #     print(str(device_id)==str(devid))
        # print("device_id", device_id)
        
        # device = device_manager.get_device(device_id)
        # print("device=",device)
        device_id = uuid.UUID(device_id)
        if device := await device_manager.get_device(device_id):
            await device.sample()
        else:
            logger.error(f"{device_id} non found.")
    
    logger.info("sample finished")




async def polling_device():
    logger.info(f"polling_device start.")
    concurrent_tasks = []  # (device_id, coroutine)
    sequential_tasks = []  # (device_id, coroutine_func)

    db_devices:list[Device] = await get_all_devices()
    for db_device in db_devices:
        if not db_device.enabled: continue
        device = await device_manager.get_device(db_device.id)
        if not device: continue
        if db_device.protocol.lower() in ["modbusrtu", "modbustcp"]:
            sequential_tasks.append( (db_device.name, device.sample) )
        else:
            concurrent_tasks.append( (db_device.name, device.sample) )
    
    async def run_concurrent():
        results = await asyncio.gather(
            *[task() for _, task in concurrent_tasks],
            return_exceptions=True
        )

        for (device_id, _), result in zip(concurrent_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"[并发] 设备 {device_id} 执行失败: {str(result)}")
            else:
                logger.info(f"[并发] 设备 {device_id} 采样完成")


    async def run_sequential():
        for device_id, sample in sequential_tasks:
            try:
                logger.debug(f"[顺序] 执行设备 {device_id}")
                await sample()
            except Exception as e:
                logger.error(f"[顺序] 设备 {device_id} 执行失败: {str(e)}")
            else:
                logger.info(f"[顺序] 设备 {device_id} 完成")
    
    await asyncio.gather(
        run_concurrent(),
        run_sequential()
    )
    
    logger.info("polling_device finished.")

async def monitor_db():
    logger.info("monitor_db start")
    await trim_points_for_metric(
        max_points=100,
    )
    logger.info("monitor_db finished")


async def polling_bacnet_device(ttl:int):
    logger.info(f"polling_bacnet start with {ttl}.")
    concurrent_tasks = []  # (device_id, coroutine)
    db_devices:list[Device] = await get_all_devices()
    for db_device in db_devices:
        if not db_device.enabled: continue
        device = await device_manager.get_device(db_device.id)
        if not device: continue
        if db_device.protocol.lower() in ["bacnet"]:
            concurrent_tasks.append( (db_device.name, device.sample) )
    
    async def run_concurrent(ttl):
        results = await asyncio.gather(
            *[task(ttl) for _, task in concurrent_tasks],
            return_exceptions=True
        )

        for (device_id, _), result in zip(concurrent_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"[并发] 设备 {device_id} 执行失败: {str(result)}")
            else:
                logger.info(f"[并发] 设备 {device_id} 采样完成")

    await asyncio.gather(run_concurrent(ttl))
    
    logger.info("polling_device finished.")


async def polling_modbus_device(ttl:int):
    logger.info(f"polling_modbus start with {ttl}.")

    sequential_tasks = []  # (device_id, coroutine_func)
    db_devices:list[Device] = await get_all_devices()
    for db_device in db_devices:
        if not db_device.enabled: continue
        device = await device_manager.get_device(db_device.id)
        if not device: continue
        if db_device.protocol.lower() in ["modbusrtu", "modbustcp"]:
            sequential_tasks.append( (db_device.name, device.sample) )

    async def run_sequential(ttl):
        for device_id, sample in sequential_tasks:
            try:
                logger.debug(f"[顺序] 执行设备 {device_id}")
                await sample(ttl)
            except Exception as e:
                logger.error(f"[顺序] 设备 {device_id} 执行失败: {str(e)}")
            else:
                logger.info(f"[顺序] 设备 {device_id} 完成")
    
    await asyncio.gather(run_sequential(ttl))
    
    logger.info("polling_modbus finished.")