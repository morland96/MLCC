<template>
    <div>
        <Row :gutter="5">
            <Col :span="14">
            <Row :gutter="5">
                <Card>
                    <p slot="title">
                        使用指南
                    </p>
                    <img src="@/assets/b.jpg" class="banner">
                </Card>
            </Row>
            </Col>
            <Col :span="10">
            <Row>
                <Card>
                    <p slot="title">
                        用户信息
                    </p>
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
            <Row style="margin-top:10px">
                <Card style="text-align: center">
                    <p slot="title" style="text-align: left">
                        集群状态
                    </p>
                    <table class="info">
                        <tr>
                            <td>集群位置：</td>
                            <td> 生科</td>
                        </tr>
                        <tr>
                            <td>主服务器IP：</td>
                            <td> 219.216.67.203</td>
                        </tr>
                        <tr>
                            <td>当前节点机数量：</td>
                            <td> {{status.length}}</td>
                        </tr>
                        <tr>
                            <td> 总进程数量： </td>
                            <td> {{(status.length)*10}}</td>
                        </tr>
                                                <tr>
                            <td> 今日完成任务数： </td>
                            <td> {{works.length}}</td>
                        </tr>
                    </table>
                </Card>
            </Row>
            </Col>

        </Row>
    </div>
</template>

<script>
import avator from '../../assets/logo.png'
import b from '../../assets/b.jpg'
export default {
  components: {},
  data () {
    return {
      status: null,
      works: null
    }
  },
  created () {
    this.axios.get('/api/nodes/status').then(response => {
      let data = response.data
      this.status = data.reverse()
      this.$Loading.finish()
    })
    this.axios.get('/api/works').then(response => {
      let data = response.data
      this.works = data.reverse()
      this.$Loading.finish()
    })
  },
  mounted () {
    this.$nextTick(() => {
      let iframe = document.getElementById('directory_view')
      console.log(this.$refs['directory_view'].contentWidow)
      console.log(iframe.contentWidow)
    })
  },
  computed: {
    avator () {
      return avator
    },
    b () {
      return b
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
.banner {
  width: 100%;
}
.info {
  text-align: center;
  padding-right: 70px;
  padding-left: 70px;
  width: 100%;
  tr {
    text-align: center;
    td {
      text-align: center;
    }
  }
}
</style>
