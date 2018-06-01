<style lang="less" scoped>
@import "./Login.less";
</style>

<template>
  <div class="login" @keydown.enter="handleSubmit">
    <div class="login-con">
      <Card :bordered="false">
        <p slot="title">
          <Icon type="log-in"></Icon>
          欢迎登录
        </p>
        <div class="form-con">
          <Form ref="loginForm" :model="form">
            <FormItem prop="userName">
              <i-input v-model="form.username" placeholder="请输入用户名">
                <span slot="prepend">
                  <Icon :size="16" type="person"></Icon>
                </span>
              </i-input>
            </FormItem>
            <FormItem prop="password">
              <i-input type="password" v-model="form.password" placeholder="请输入密码">
                <span slot="prepend">
                  <Icon :size="14" type="locked"></Icon>
                </span>
              </i-input>
            </FormItem>
            <FormItem>
              <Button @click="handleSubmit" type="primary" long>登录</Button>
            </FormItem>
          </Form>
        </div>
      </Card>
    </div>
  </div>
</template>
<style>

</style>

<script>
export default {
  data () {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    handleSubmit () {
      this.axios
        .post('/api/sessions', {
          username: this.form.username,
          password: this.form.password
        })
        .then(
          function (response) {
            this.$Message.success('Login succcess')
            console.log(response)
            let token = response['data']['token']
            let user = response['data']['user']
            let redirect = decodeURIComponent(
              this.$route.query.redirect || '/'
            )
            this.$store.commit('login', { token: token, user: user })
            this.$router.push({
              path: redirect,
              force: true
            })
          }.bind(this)
        )
        .catch(error => {
          console.log(error.response)
          this.$Message.error(`用户名或密码错误`)
        })
    }
  }
}
</script>
