<template>
  <Row class="scripts">
    <Poptip trigger='hover' placement="right" :title="'代码包名：'+script.script_name">
      <i-col :span="6">
        <Icon type="ios-paper" :size="64"></Icon>
      </i-col>
      <i-col :span="18" class="right-info">
        <p class="script-name" v-text="script.script_name" />
        <p class="uuid" v-text="script.uuid" />
      </i-col>
      <div slot="content" class="info">
        <p>
          <span class="info-title">ID:</span> {{script.uuid}}</p>
        <p>
          <span class="info-title">使用语言:</span> {{script.language}}</p>
        <p>
          <span class="info-title">上传者:</span> {{script.uploader}}</p>
        <p>
          <span class="info-title">上传时间:</span> {{renderTime(script.upload_time)}}</p>
        <p>
          <span class="info-title">详细信息:</span> {{script.details}}</p>
        <span class="info-button">
          <Button type="text" @click="showScript()">查看主程序</Button>
          <Button type="text" @click="remove()">删除</Button>
        </span>
      </div>
    </Poptip>
  </Row>
</template>
<script>
export default {
  data () {
    return {}
  },
  methods: {
    renderTime (timestr) {
      var time = new Date(timestr)
      return `${time.getMonth()}月${time.getDate()}号 ${time.getHours()}:${time.toLocaleTimeString(
        [],
        { hour: '2-digit', minute: '2-digit' }
      )}`
    },
    remove () {
      this.axios
        .delete(`/api/scripts/${this.script.uuid}`)
        .then(response => {
          this.$Notice.success({
            title: '数据删除成功'
          })
          this.$emit('update')
        })
        .catch(error => {
          this.$Message.error('删除错误')
          console.log(error)
        })
    },
    showScript () {
      this.axios.get(`/api/scripts/${this.script.uuid}/main`).then(response => {
        let scriptContent = response.data['content']
        this.$emit('showScript', scriptContent)
      })
    }
  },
  props: ['script']
}
</script>
<style lang="less" scoped>
.right-info {
  padding-left: 10px;
  vertical-align: middle;
  padding-top: 8px;
}
.scripts {
  padding-bottom: 20px;
}
.script_name {
  font-size: 14px;
}
.uuid {
  font-size: 10px;
  color: green;
}
.info-title {
  padding-right: 5px;
  color: black;
}
.info {
  color: gray;
}
.info-button {
  text-align: center;
  padding-left: 10px;
  margin-bottom: 10px;
}
</style>
