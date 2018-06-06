<template>

    <Row :gutter="10">
        <Col :span="10">
        <Row>
            <Card>
                <p slot="title">
                    用户信息
                </p>
                <div slot="extra">
                    <Button type="text" @click="changePassword">修改密码</Button>
                    <Button type="text" @click="createAccount" v-if="privilege=='管理员'">创建新的用户</Button>
                </div>
                <Row type="flex" class="user-info">
                    <Col span="8">
                    <Row type="flex" class-name="made-child-con-middle" align="middle">
                        <img :src="avator" class="avator-img">
                    </Row>
                    </Col>
                    <Col span="16" style="padding-left:6px;">
                    <Row type="flex" class-name="made-child-con-middle" align="middle">
                        <div>
                            <h3>欢迎登陆多语言医疗影像计算系统</h3>
                            <p>当前用户： {{user.username}}</p>
                            <p>当前身份： {{privilege}}</p>
                            <p>登陆地点： 沈阳</p>
                        </div>
                    </Row>
                    </Col>

                </Row>

            </Card>
        </Row>
        </Col>
        <Col :span="14" v-if="showChangePassword">
        <Card>
            <Form label-width="80">
                <FormItem label="当前密码">
                    <Input type="password"  placeholder="请输入密码" />
                </FormItem>
                <FormItem label="新的密码">
                    <Input type="password"  placeholder="请输入密码" />
                </FormItem>
                <FormItem>
                    <Button type="primary" @click="submitChangePassword"> 提交 </Button>
                </FormItem>
            </Form>
        </Card>
        </Col>
        <Col :span="14" v-if="showCreateAccount">
        <Card>
            <Form :model="account" label-width="80">
                <FormItem label="用户名">
                    <Input v-model="account.username" placeholder="请输入用户名" />
                </FormItem>
                <FormItem label="密码">
                    <Input type="password" v-model="account.password" placeholder="请输入密码" />
                </FormItem>
                <FormItem label="权限">
                    <Select v-model="account.right" placeholder="请输入分配的权限">
                        <Option value="0"> 管理员 </Option>
                        <Option value="1"> 普通用户 </Option>
                    </Select>
                </FormItem>
                <FormItem>
                    <Button type="primary" @click="submitCreateAccount"> 提交 </Button>
                </FormItem>
            </Form>
        </Card>
        </Col>
    </Row>
</template>

<script>
import avator from '../../assets/logo.png'
export default {
  data () {
    return {
      showChangePassword: false,
      showCreateAccount: false,
      account: {
        username: '',
        password: '',
        right: ''
      }
    }
  },
  computed: {
    avator () {
      return avator
    },
    user () {
      return this.$store.state.UserInfo.user
    },
    privilege () {
      if (this.user.privilege === '0') {
        return '管理员'
      } else {
        return '普通用户'
      }
    }
  },
  methods: {
    changePassword () {
      this.showChangePassword = true
      this.showCreateAccount = false
    },
    createAccount () {
      this.showCreateAccount = true
      this.showChangePassword = false
    },
    submitChangePassword () {
      this.$Notice.success({
        title: '成功',
        desc: `修改密码成功`
      })
    },
    submitCreateAccount () {
      this.axios
        .post('/api/users', {
          username: this.account.username,
          password: this.account.password,
          privilege: this.account.right
        })
        .then(() => {
          this.$Notice.success({
            title: '创建成功',
            desc: `创建用户, ${this.account.username}`
          })
          this.showCreateAccount = false
        })
    }
  }
}
</script>
<style lang="less">
.user-info {
  height: 150;
}
.avator-img {
  display: block;
  width: 80%;
  max-width: 150px;
  height: auto;
}
.made-child-con-middle {
  height: 100%;
}
</style>
