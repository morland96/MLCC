<style>
@import "./scripts.css";
</style>

<template>
  <Card dis-hover>
    <Row>
      <Col :span="10">
      <Card>
        <Row>
          <i-col :span="12" v-for="script in scripts" :key="script.uuid">
            <scriptMini :script="script" @update="updateTable" @showScript="showScript" />
          </i-col>
          <i-col :span="12">
            <template>
              <Row>
                <Upload ref="upload" class="upload" action="/api/upload_script" :on-success="handleSuccess">
                  <i-col :span="8">
                    <Button class="upload-button" type="ghost">
                      <Icon type="ios-cloud-upload-outline" :size="20"> </Icon>
                    </Button>
                  </i-col>
                  <i-col :span="16">
                    <p class="upload-desc">点击按钮上传代码包</p>
                  </i-col>
                </Upload>
              </Row>
            </template>
          </i-col>
        </Row>
      </Card>
      </Col>
      <Col :span="14" class="padding-left-10">
      <Card v-if="showUploadForm">
        <Form ref="uploadForm" :model="uploadForm" :label-width="80">
          <FormItem label="代码ID" prop="uuid">
            <Input v-model="uploadForm.uuid" placeholder="上传文件后自动填充" disabled/>
          </FormItem>
          <FormItem label="名称" prop="script_name">
            <Input v-model="uploadForm.script_name" placeholder="请输入文件名称" />
          </FormItem>
          <FormItem label="代码语言" prop="language">
            <Select v-model="uploadForm.language" placeholder="请选择语言">
              <Option value="Python"> Python</Option>
              <Option value="Matlab">Matlab</Option>
            </Select>
          </FormItem>
          <FormItem label="描述" prop="details">
            <Input v-model="uploadForm.details" type="textarea" :row="4" placeholder="请输入描述" />
          </FormItem>

          <FormItem>
            <Button type="primary" @click="submit()">保存</Button>
          </FormItem>
        </Form>
      </Card>
      <Card v-if="showScriptCard" class="code">
      <pre><code v-html="code" class="language-python"/>
      </pre>
      </Card>
      </Col>
    </Row>
  </Card>
</template>
<script>
import scriptMini from '../custom-components/scripts-mini.vue'
export default {
  components: {
    scriptMini
  },
  data () {
    return {
      scripts: [],
      uploadForm: {
        script_name: '',
        uuid: '',
        details: '',
        language: ''
      },
      showUploadForm: false,
      showScriptCard: false,
      loading: false,
      code: ''
    }
  },
  created () {
    this.updateTable()
  },
  methods: {
    updateTable () {
      this.$Loading.start()
      this.axios.get('/api/scripts').then(response => {
        let data = response.data
        this.scripts = data.reverse()
        this.$Loading.finish()
      })
    },
    handleSuccess (evnet, file) {
      let response = JSON.parse(event['currentTarget']['response'])

      this.$Notice.success({
        title: '文件上传成功',
        desc: '文件 ' + file.name + ' 上传成功。请填写相关信息'
      })
      this.uploadForm.uuid = response['uuid']
      this.showScriptCard = false
      this.showUploadForm = true
    },
    submit () {
      this.$Loading.start()
      this.axios
        .post('/api/script', {
          uuid: this.uploadForm.uuid,
          script_name: this.uploadForm.script_name,
          details: this.uploadForm.details,
          language: this.uploadForm.language
        })
        .then(response => {
          this.$Loading.finish()
          this.$Message.success('保存成功')
          this.$refs['upload'].clearFiles()
          this.updateTable()
        })
        .catch(error => {
          console.log('get error')
          console.log(error.response)
          this.$Message.error(error)
          this.loading = true
        })
    },
    showScript (script) {
      this.showUploadForm = false
      this.showScriptCard = true
      let html = this.Prism.highlight(
        script,
        this.Prism.languages.python,
        'python'
      )
      this.code = html
    }
  }
}
</script>
<style lang="less" scoped>
.upload-button {
  width: 48px;
  height: 48px;
}
.upload {
  padding-top: 5px;
  p {
    font-size: 12px;
    padding: 4px;
  }
}
.padding-left-10 {
  padding-left: 10px;
}
.code {
  background: #2d2d2d;
}
</style>
