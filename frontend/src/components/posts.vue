<template>
  <div class="hello">
    <img src='@/assets/logo-django.png' style="width: 250px" />
    <p>The data below is added/removed from the SQLite Database using Django's ORM and Rest Framework.</p>
    <br/>
    <p>Subject</p>
    <input type="text" placeholder="Hello" v-model="title">
    <p>Body</p>
    <input type="text" placeholder="From the other side" v-model="postBody">
    <br><br>
    <input
      type="submit"
      value="Add"
      @click="addPost({ title: title, body: postBody })"
      :disabled="!title || !postBody">

    <hr/>
    <h3>Posts on Database</h3>
    <p v-if="posts.length === 0">No Posts</p>
    <div class="post" v-for="(post, index) in posts" :key="index">
        <p class="post-index">[{{index}}]</p>
        <p class="post-title" v-html="post.title"></p>
        <p class="post-body" v-html="post.body"></p>
        <input type="submit" @click="deletePost(post.pk)" value="Delete" />
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
export default {
  name: "Posts",
  data() {
    return {
      title: "",
      postBody: "",
    };
  },
  computed: mapState({
    posts: state => state.posts.posts
  }),
  methods: mapActions('posts', [
    'addPost',
    'deletePost'
  ]),
  created() {
    this.$store.dispatch('posts/getPosts')
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
hr {
  max-width: 65%;
}
.post {
  margin: 0 auto;
  max-width: 30%;
  text-align: left;
  border-bottom: 1px solid #ccc;
  padding: 1rem;
}
.post-index {
  color: #ccc;
  font-size: 0.8rem;
  /* margin-bottom: 0; */
}
img {
  width: 250px;
  padding-top: 50px;
  padding-bottom: 50px;
}
</style>
