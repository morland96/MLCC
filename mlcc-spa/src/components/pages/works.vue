<template>
    <div>
        <Row>

            <Card>
                <Tabs value="status">
                    <TabPane label="集群信息： 生科" name="status">
                        <Row>
                            <Col :span="8" ref="cpu_usage_col">
                            <div id="cpu_usage" ref="cpu_usage" style="width:100%"></div>
                            </Col>
                            <Col :span="8">
                            <div id="cpu_history" ref="cpu_history" style="width:100%"></div>
                            </Col>
                            <Col :span="8">
                            <Col>
                            <Row type="flex" justify="center" align="middle" ref="cluster_status" class="cluster-row">
                                <table class="cluster-status">
                                    <tr style="display:table-caption">
                                        <img :src="logo" width="160px" />
                                    </tr>
                                    <tr>
                                        <td class="title">当前集群状态：</td>
                                        <td style="color:green">正常</td>
                                    </tr>
                                    <tr>
                                        <td class="title">执行中的任务：</td>
                                        <td>{{runningWorks}}</td>
                                    </tr>
                                    <tr>
                                        <td class="title">中央服务器IP：</td>
                                        <td>219.216.67.203</td>
                                    </tr>
                                </table>
                            </Row>
                            </Col>

                            </Col>
                        </Row>
                    </TabPane>
                    <TabPane label="创建任务" name="create_work">
                        <Row>
                            <Col :span="11">
                            <Form :model="workForm" :label-width="80">
                                <FormItem label="任务名称" prop="work_name">
                                    <Input v-model="workForm.work_name" placeholder="填写任务名称" />
                                </FormItem>
                                <FormItem label="分包大小" prop="batch_size">
                                    <InputNumber :max="255" :min="1" v-model="workForm.batch_size" placeholder="填写分包大小" />
                                </FormItem>
                                <FormItem label="描述" prop="details">
                                    <Input v-model="workForm.details" type="textarea" :row="4" placeholder="请输入描述" :autosize="{minRows: 8,maxRows: 8}" />
                                </FormItem>

                            </Form>
                            </Col>
                            <Col :span="11" :offset="2">

                            <Form :model="workForm">
                                <FormItem :label="'数据集:'+workForm.dataset_id" prop="dataset_id">
                                    <p slot="label">数据集:
                                        <span v-text="workForm.dataset_id" class="gray-label" />
                                    </p>
                                    <Select v-model="workForm.dataset_id" placeholder="请选择数据集" filterable>
                                        <Option v-for="dataset in datasets" :key="dataset.uuid" :value="dataset.uuid" :label="dataset.filename">
                                            <Tooltip trigger="hover" placement="right">
                                                <p slot="content" v-text="dataset.details" />
                                                <span v-text="dataset.filename" />
                                            </Tooltip>
                                            <span style="float:right;color:#ccc" v-text="dataset.uuid" />
                                        </Option>
                                    </Select>
                                </FormItem>
                                <FormItem label="代码" prop="script_id">
                                    <p slot="label">代码:
                                        <span v-text="workForm.script_id" class="gray-label" />
                                    </p>
                                    <Select v-model="workForm.script_id" placeholder="请选择代码" filterable>

                                        <Option v-for="script in scripts" :key="script.uuid" :value="script.uuid" :label="script.script_name">

                                            <Tooltip trigger="hover" placement="right">
                                                <p slot="content" v-text="script.details" />
                                                <span v-text="script.script_name" />
                                            </Tooltip>
                                            <span style="float:right;color:#ccc" v-text="script.uuid" />
                                        </Option>
                                    </Select>
                                </FormItem>
                                <Button type="success" long @click="clickSubmit()">提交</Button>
                                <Modal v-model="submitModal" title="确认请求" :loading="true" ref="submitModal" :ok-text="okText" @on-ok="submit">

                                    <tr>
                                        <td>任务名: </td>
                                        <td>{{workForm.work_name}}</td>
                                    </tr>
                                    <tr>
                                        <td>代码ID: </td>
                                        <td>{{workForm.script_id}}</td>
                                    </tr>
                                    <tr>
                                        <td>数据ID: </td>
                                        <td>{{workForm.dataset_id}}</td>
                                    </tr>
                                </Modal>
                            </Form>
                            </Col>
                        </Row>
                    </TabPane>
                </Tabs>
            </Card>

        </Row>
        <Row>
            <Col :span="8" v-for="work in works" :key="work.uuid">
            <works-card :work="work" @showMore="showMore" />
            </Col>
        </Row>
        <Modal v-model="showMoreModal" width="90%" :styles="{top:'10px'}" :closable="false">
            <iframe :src="showMoreSrc" frameborder='0' width="100%" height="670px">
            </iframe>
            <div slot="footer">
                <Button @click="download" type="info">下载</Button>
                <Button @click="del" type="error">删除</Button>
                <Button @click="showMoreModal = false" >关闭</Button>
            </div>
        </Modal>
    </div>
</template>
<script>
import worksCard from '../custom-components/works-card.vue'
import logo from '../../assets/logo.png'
let echarts = require('echarts/lib/echarts')
require('echarts/lib/component/tooltip')
require('echarts/lib/component/title')
require('echarts/lib/component/axis')
require('echarts/lib/component/timeline')
require('echarts/lib/chart/gauge')
require('echarts/lib/chart/line')

export default {
  components: {
    worksCard
  },
  data () {
    return {
      works: [],
      status: [],
      workForm: {
        work_name: '',
        script_id: '',
        dataset_id: '',
        batch_size: 2,
        details: ''
      },
      runningWorks: 0,
      old_unfinished: [],
      unfinished: [],
      showMoreModal: false,
      showing_uuid: '',
      cpuHistory: [],
      cpuChart: null,
      historyChart: null,
      recalcHandle: null,
      loading: true,
      scripts: null,
      datasets: null,
      submitModal: false,
      showMoreSrc: '',
      okText: '部署'
    }
  },
  computed: {
    totalNodeWorkLoad () {
      var totalCPU = 0
      let nodeStatus = this.status
      let nodeNum = nodeStatus.length
      for (let i = 0; i < nodeNum; i++) {
        totalCPU += nodeStatus[i]['cpu_usage']
      }
      return Math.round(totalCPU / nodeNum)
    },
    logo () {
      return logo
    }
  },

  mounted () {
    this.$nextTick(() => {
      let len = this.$refs.cpu_usage.offsetWidth * 0.8
      this.cpuChart.resize({ width: len, height: len })
      this.historyChart.resize({ width: len, height: len })
    })
    this.updateTable()
    clearTimeout(this.recalcHandle)
    this.drawCpuUsage()
    this.drawHistoryChart()
  },
  deactivated () {
    console.log('quit this router view')
    clearTimeout(this.recalcHandle)
  },
  activated () {
    this.updateCpuUsage()
    this.axios.get('/api/scripts').then(response => {
      let data = response.data
      this.scripts = data.reverse()
    })
    this.axios.get('/api/datasets').then(response => {
      let data = response.data
      this.datasets = data.reverse()
    })
  },
  methods: {
    showMore (uuid) {
      this.showMoreSrc = '/directory/works_result/' + uuid
      this.showing_uuid = uuid
      this.showMoreModal = true
    },
    download () {
      window.open('/directory/works_result/' + this.showing_uuid + '.tar.gz')
    },
    clickSubmit () {
      this.submitModal = true
      this.okText = '部署'
    },
    submit () {
      let workForm = this.workForm
      this.okText = '部署中'
      this.axios
        .post('/api/works', {
          work_name: workForm.work_name,
          batch_size: workForm.batch_size,
          dataset_id: workForm.dataset_id,
          script_id: workForm.script_id,
          details: workForm.details
        })
        .then(response => {
          setTimeout(() => {
            this.submitModal = false
            this.okText = '部署完毕'
          }, 500)
          this.updateTable()
        })
    },
    updateTable () {
      this.old_unfinished = this.unfinished
      this.axios.get('/api/works').then(response => {
        let data = response.data
        this.works = data.reverse()
        let runningWorks = 0
        let unfinished = []
        for (let i in this.works) {
          let work = this.works[i]
          if (work.finished_time === '') {
            runningWorks += 1
            unfinished.push(work.uuid)
          }
        }
        this.runningWorks = runningWorks
        this.unfinished = unfinished
        for (let i in this.old_unfinished) {
          let result = false
          let uuid = this.old_unfinished[i]
          for (let i in this.unfinished) {
            if (this.unfinished[i] === uuid) result = true
          }
          if (result) {
            console.log(this.old_unfinished[i] + ' still running')
          } else {
            console.log(this.old_unfinished[i] + ' is Done')
            this.$Notice.success({
              title: '任务执行完毕',
              desc: '任务ID: ' + this.old_unfinished[i] + ' 已完成'
            })
          }
        }
      })
    },
    updateCpuUsage () {
      this.axios.get('/api/nodes/status').then(response => {
        let data = response.data
        this.status = data
        let currentUsage = this.totalNodeWorkLoad
        let now = new Date()
        this.cpuHistory.push({
          name: now.toString(),
          value: [now.toISOString(), currentUsage]
        })
        if (this.cpuHistory.length > 10) {
          this.cpuHistory.shift()
        }
        this.historyChart.setOption({
          series: [
            {
              data: this.cpuHistory
            }
          ]
        })
        this.cpuChart.setOption({
          series: [
            {
              data: [
                { value: currentUsage, name: '' }
                // { value: 100 - currentUsage, name: '空闲' }
              ]
            }
          ]
        })
        this.startRecalc()
      })
    },
    startRecalc () {
      clearTimeout(this.recalcHandle)
      this.recalcHandle = setTimeout(this.updateInfo, 3000)
    },
    updateInfo () {
      this.updateCpuUsage()
      this.updateTable()
    },
    drawCpuUsage () {
      let cpuChart = echarts.init(document.getElementById('cpu_usage'))
      this.cpuChart = cpuChart
      cpuChart.setOption({
        title: {
          text: '集群负载状态',
          x: 'center',
          y: 'bottom',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {},
        series: [
          {
            type: 'gauge',
            detail: { formatter: '{value}%' },
            hoverAnimation: false,
            data: [50],
            itemStyle: {
              emphasis: {
                shadowBlur: 10,
                shadowColor: 'rgba(0,0,0,0.5)'
              }
            }
          }
        ]
      })
      this.loading = false
    },
    drawHistoryChart () {
      let historyChart = echarts.init(document.getElementById('cpu_history'))
      this.historyChart = historyChart
      historyChart.setOption({
        title: {
          text: '负载历史',
          x: 'center',
          y: 'bottom',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            params = params[0]
            let date = new Date(params.value[0])
            return (
              date.getHours() +
              ':' +
              date.getMinutes() +
              ':' +
              date.getSeconds() +
              ' : ' +
              params.value[1] +
              '%'
            )
          },
          axisPointer: {
            animation: false
          }
        },
        yAxis: {
          type: 'value',
          max: 100,
          min: 0,
          splitLine: {
            show: false
          }
        },
        xAxis: {
          type: 'time',

          splitLine: {
            show: false
          }
        },
        series: [
          {
            name: '折线图',
            type: 'line',
            symbolSize: 4,
            hoverAnimation: false,
            data: this.cpuHistory
          }
        ]
      })
      this.loading = false
    }
  }
}
</script>
<style lang="less">
#cpu_usage {
  width: 100%;
}
.cluster-row {
  border-left: 1px solid #e9eaec;
}
.cluster-status {
  margin: 40px;
  height: 100%;
  text-align: center;
  font-weight: 300;
  color: #616366;
  font-size: 16px;

  img {
    margin-bottom: 20px;
  }
  .title {
    padding-right: 20px;
    font-weight: 500;
    font-size: 16px;
  }
}
.gray-label {
  color: gray;
}
</style>
