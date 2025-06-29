import uuid
from datetime import datetime
from ..schemas import ResponseModel, ProjectCreate
from ...db.database import get_session, AsyncSession
from ...db.models import Project

from typing import List
from sqlmodel import select, delete, func
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/iot", tags=["Project"])


@router.post("/project", response_model=ResponseModel, status_code=200)
async def create_project(porject: ProjectCreate, session: AsyncSession = Depends(get_session)):
    db_project = Project.model_validate(porject)
    db_project.time = datetime.now()
    try:
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)
        return {"status":"OK", "data":db_project}
    except Exception as e:
        await session.rollback()
        return {"status":"FAIL", "data":"point already exists"}

@router.get("/projects", response_model=ResponseModel, status_code=200)
async def get_all_projects(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Project))
    projects = result.scalars().all()
    return {"status":"OK", "data":list(projects)}    

@router.get("/project/{project_id}", response_model=ResponseModel, status_code=200)
async def get_project_by_id(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    project = await session.get(Project, project_id)
    return {"status":"OK", "data":project}

@router.delete("/project/{project_id}")
async def delete_project_by_id(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    protject = await session.get(Project, project_id)
    if protject:
        await session.delete(protject)
        await session.commit()
        return {"status":"OK", "data":protject}
    return {"status":"FAIL", "data":f"{project_id} not found"}


@router.patch("/project/{project_id}", response_model=ResponseModel, status_code=200)
async def update_project(project_id: uuid.UUID, project_update: dict, session: AsyncSession = Depends(get_session)):
    project = await session.get(Project, project_id)
    if not project:
        return {"status":"FAIL", "data":f"{project_id} not found"}

    for key, value in project_update.items():
        setattr(project, key, value)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return {"status":"OK", "data":project}

