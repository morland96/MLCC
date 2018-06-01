<template>
  <div>
    <Row>
      <i-col span="14">
        <Card>
          <Row>
            <Table stripe highlight-row :columns="columns" :loading="loading" :data="data_set" height="600"></Table>
          </Row>
        </Card>
      </i-col>
      <i-col span="10" class="padding-left-10">
        <Card>
          <Form ref="uploadForm" :model="uploadForm" :rules="ruleValidate">
            <FormItem label="名称" prop="filename">
              <Input v-model="uploadForm.filename" placeholder="请输入文件名称" />
            </FormItem>
            <FormItem label="描述">
              <Input v-model="uploadForm.details" type="textarea" :row="4" placeholder="请输入描述" />
            </FormItem>
            <FormItem label="数据ID" prop="uuid">
              <Input v-model="uploadForm.uuid" placeholder="上传文件后自动填充" disabled/>
            </FormItem>
            <Upload type="drag" action="/api/upload" :on-success="handleSuccess">
              <div style="padding: 20px 0">
                <Icon type="ios-cloud-upload" size="52" style="color: #3399ff"></Icon>
                <p>拖拽至此上传文件</p>
              </div>
            </Upload>
            <FormItem>
              <Button type="primary" @click="submit()">提交</Button>
            </FormItem>
          </Form>
        </Card>
      </i-col>
    </Row>
    <Modal v-model="showMoreModal" width="90%" :styles="{top:'10px'}" :closable="false">
      <iframe :src="showMoreSrc" frameborder='0' width="100%" height="670px">
      </iframe>
      <div slot="footer">
        <Button @click="showMoreModal = false" type="error">关闭</Button>
      </div>
    </Modal>
  </div>
</template>
<script>
export default {
  data () {
    return {
      loading: true,
      uploadForm: {
        filename: '',
        details: '',
        uuid: ''
      },
      showMoreModal: false,
      showMoreSrc: '',
      ruleValidate: {
        filename: [
          {
            required: true,
            message: '文件名不能为空',
            trigger: 'blur'
          }
        ],
        uuid: [
          {
            required: true,
            message: '请先上传文件',
            trigger: 'blur'
          }
        ]
      },
      columns: [
        {
          title: '数据ID',
          key: 'uuid',
          width: 200
        },
        {
          title: '名称',
          key: 'filename',
          fixed: 'left',
          width: 100,
          render: (h, params) => {
            return h('div', [
              h('Icon', {
                props: {
                  type: 'filing'
                }
              }),
              h('strong', ' ' + params.row.filename)
            ])
          }
        },
        {
          title: '上传时间',
          key: 'upload_time',
          className: 'green',
          width: 160,
          render: (h, params) => {
            return h('span', this.renderTime(params.row.upload_time))
          }
        },
        {
          title: '描述',
          key: 'details',
          width: 200,
          ellipsis: true,
          render: (h, params) => {
            return h(
              'Tooltip',
              {
                props: {
                  trigger: 'hover',
                  transfer: false,
                  placement: 'left'
                }
              },
              [
                h(
                  'div',
                  {
                    slot: 'content',
                    style: {
                      whiteSpace: 'normal',
                      wordBreak: 'normal'
                    }
                  },
                  this.data_set[params.index]['details']
                ),
                h(
                  'span',
                  {
                    style: {
                      display: 'inline-block',
                      width: '150px',
                      textOverflow: 'ellipsis',
                      overflow: 'hidden',
                      whiteSpace: 'nowrap'
                    }
                  },
                  params.row.details
                )
              ]
            )
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 70,
          className: 'action',
          align: 'center',
          fixed: 'right',
          render: (h, params) => {
            return h('div', [
              h(
                'Button',
                {
                  props: {
                    type: 'text'
                  },
                  on: {
                    click: () => {
                      this.show(params.index)
                    }
                  }
                },
                '查看'
              ),
              h(
                'Poptip',
                {
                  props: {
                    confirm: true,
                    title: '您确定要删除这条数据吗?',
                    transfer: true
                  },
                  on: {
                    'on-ok': () => {
                      this.delete(params.index)
                    }
                  }
                },
                [
                  h(
                    'Button',
                    {
                      style: {},
                      props: {
                        type: 'text',
                        placement: 'top'
                      }
                    },
                    '删除'
                  )
                ]
              )
            ])
          }
        }
      ],
      data_set: []
    }
  },
  created () {
    this.loading = true
    this.updateTable()
  },
  methods: {
    show (index) {
      this.showMoreModal = true
      this.showMoreSrc = '/directory/upload/datasets/' + this.data_set[index]['uuid']
    },
    updateTable () {
      this.axios.get('/api/datasets').then(response => {
        let data = response.data
        this.data_set = data.reverse()
        console.log(response)
        this.loading = false
      })
    },
    renderTime (timestr) {
      var time = new Date(timestr)
      return `${time.getMonth()}月${time.getDate()}号 ${time.getHours()}:${time.toLocaleTimeString(
        [],
        { hour: '2-digit', minute: '2-digit' }
      )}`
    },
    delete (index) {
      console.log(index)
      // this.data_set.splice(index, 1)
      let uuid = this.data_set[index]['uuid']
      this.axios
        .delete(`/api/datasets/${uuid}`)
        .then(response => {
          this.$Notice.success({
            title: '数据删除成功',
            desc: uuid + '已删除'
          })
          this.updateTable()
        })
        .catch(error => {
          this.$Message.error('删除错误')
          console.log(error)
        })
    },
    handleSuccess (evnet, file) {
      this.$Notice.success({
        title: '文件上传成功',
        desc: '文件 ' + file.name + ' 上传成功。'
      })
      let response = JSON.parse(event['currentTarget']['response'])
      this.uploadForm.uuid = response['uuid']
    },
    submit () {
      this.loading = true
      this.$refs['uploadForm'].validate(valid => {
        if (!valid) {
          this.$Message.error('请检查表格')
          return 0
        } else {
          this.axios
            .post('/api/datasets', {
              filename: this.uploadForm.filename,
              details: this.uploadForm.details,
              uuid: this.uploadForm.uuid
            })
            .then(response => {
              this.$Message.success('数据上传成功')
              console.log(response)
              this.updateTable()
              this.uploadForm.uuid = ''
            })
            .catch(error => {
              console.log('get error')
              console.log(error.response)
              this.$Message.error(error)
              this.loading = true
            })
        }
      })
    }
  }
}
</script>
<style lang="less">
.ivu-table-row {
  .green {
    color: green;
  }
  .action {
    .ivu-table-cell {
      padding: 0px;
    }
  }
}
.padding-left-10 {
  padding-left: 10px;
}
</style>
