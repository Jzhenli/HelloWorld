<template>
  <div id="app">
    <h1>PyApp Application</h1>
    <p>Frontend is working!</p>
    <p>API Status: {{ status }}</p>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      status: 'loading...'
    }
  },
  async mounted() {
    try {
      const res = await fetch('/api/health')
      const data = await res.json()
      this.status = data.status
    } catch (e) {
      this.status = 'error'
    }
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>
