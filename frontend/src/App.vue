<template>
  <div class="app-container">
   <main class="container pt-3">
    <!-- <RouterView class="flex-shrink-0"/> -->
    <router-view class="flex-shrink-0"/>
   </main>
  </div>
</template>

<script>
// import { defineComponent } from "vue"
// import { RouterView } from "vue-router"

export default ({

  name: 'App'
  // components: {
  //   RouterView
  // },
});
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: aliceblue;
}
</style>
