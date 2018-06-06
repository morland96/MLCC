<template>
  <Row class="works-card">
    <Card :borderd="false" class="card">
      <div @click="showMore()">
        <Row>
          <Col :span="6">
          <img :src="python" width="72px" class="language-logo" v-on:click="alert()" />
          </Col>
          <Col :span="6" class="info-title">
          <h3>任务名称:
          </h3>
          <h3> 创建者: </h3>
          <h3> 创建时间: </h3>
          <h3> 详细信息: </h3>
          </Col>
          <Col :span="10" class="info-content">
          <p v-text="work.work_name" />
          <p v-text="work.user" />
          <p v-text="renderTime(work.create_time)" style="color:green" />

          <p v-text="work.details" class="details" />
          </Col>
        </Row>
      </div>

      <Row class="info-status">
        <Row class="info-status-content">
          <Col>
          <!-- <Tag type="dot" color="blue">正在运行</Tag> /-->
          <!-- <div></div> /-->
          <Col :span="8" class="right-border">
          <p class="title">运行状态</p>
          <p :style="'color:'+statusColor">{{statusText}}</p>
          </Col>
          <Col :span="8" class="right-border">
          <p class="title">进度</p>
          <p :style="'color:'+statusColor">{{progress}}
            <span style="color:green">/ {{work.data_num}}</span>
          </p>
          </Col>
          <Col :span="8">
          <p class="title">运行时长度</p>
          <p :style="'color:'+statusColor">{{finishedTime}}</p>
          </Col>
          </Col>
        </Row>
      </Row>
    </Card>
  </Row>
</template>
<script>
import pythonLogo from '../../assets/python.png'
export default {
  data () {
    return {
      processColor: 'green',
      remainTimeColor: 'red'
    }
  },
  props: ['work'],
  computed: {
    python () {
      return pythonLogo
    },
    progress () {
      let progressList = this.work.progress
      let progress = 0
      for (let p in progressList) {
        progress += progressList[p]
      }
      return progress
    },
    finishedTime () {
      let finishedTime = new Date(this.work.finished_time).getTime()
      let createTime = new Date(this.work.create_time).getTime()
      if (isNaN(finishedTime)) {
        return '运行中'
      }
      let d = finishedTime - createTime
      let min = Math.floor(d / (1000 * 60))
      let sec = Math.floor((d - min * (1000 * 60)) / 1000)
      if (sec === 0 && min === 0) {
        sec = 1
      }
      return `${min}分${sec}秒`
    },
    statusColor () {
      return this.progress === this.work.data_num ? 'green' : 'red'
    },
    statusText () {
      return this.progress === this.work.data_num ? '完成' : '运行中'
    }
  },
  methods: {
    renderTime (timestr) {
      var time = new Date(timestr)
      return `${time.getMonth()}月${time.getDate()}号 ${time.getHours()}:${time.toLocaleTimeString(
        [],
        { hour: '2-digit', minute: '2-digit' }
      )}`
    },
    showMore () {
      if (this.progress !== this.work.data_num) {
        this.$Notice.info({
          title: '程序仍在执行中请稍后',
          desc: '已执行' + this.progress + '/' + this.work.data_num
        })
      } else {
        if (this.work.user !== this.$store.state.UserInfo.user.username) {
          this.$Notice.warning({
            title: '对不起您不能查看其他用户的任务结果',
            desc: '任务属于用户： ' + this.work.user
          })
        } else {
          this.$emit('showMore', this.work.uuid)
        }
      }
    }
  }
}
</script>

<style lang="less">
.works-card {
  padding: 10px 5px;
  .title {
    margin-left: 10px;
  }
  .card {
    text-align: center;
    .language-logo {
      padding: auto;
      bottom: -5px;
    }
    img {
      margin: 10px;
    }
    .info-title {
      font-size: 14px;
      h3 {
        margin: 5px 0px;
      }
    }
    .info-content {
      color: gray;
      text-align: center;
      font-size: 16px;
      p {
        margin: 5px 0px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }
    }
    .info-status {
      display: inline-block;
      color: gray;
      text-align: center;
      width: calc(100% + 32px);
      left: -16px;
      border-top: 1px solid #e9eaec;
      margin-top: 5px;
      padding-top: 10px;
      .info-status-content {
        p {
          margin-top: 5px;
          margin-bottom: -10px;
        }
        .title {
          color: black;
          margin: 0;
        }
        .right-border {
          border-right: 1px solid #e9eaec;
        }
      }
    }
  }
}
</style>
