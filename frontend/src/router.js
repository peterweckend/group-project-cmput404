import Vue from 'vue'
import Router from 'vue-router'
import VueDemo from './components/vueDemo.vue'
import Post from './components/posts.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: VueDemo
    },
    {
      path: '/Post',
      name: 'Post',
      component: Post
    }
  ]
})