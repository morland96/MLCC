<style lang="less">
@import "./Main.less";
</style>

<template>
  <div class="main">
    <div class="sidebar-menu-con">
      <div class="logo-con">
        <b> Multi</b>LCC
      </div>
      <Menu ref="side_menu" theme="dark" width="auto" :active-name="$route.name" @on-select="onMenuSelect">
        <MenuItem name="home">
        <Icon type="document-text" /> 主页 </MenuItem>
        <MenuItem name="data-sets">
        <Icon type="document-text" /> 数据集 </MenuItem>
        <MenuItem name="scripts">
        <Icon type="document-text" /> 代码模组 </MenuItem>
        <MenuItem name="works">
        <Icon type="document-text" /> 任务 </MenuItem>
      </Menu>
    </div>
    <div class="main-header-con">
      <div class="main-header">
        <div class="header-middle-con">
          <div class="main-breadcrumb">
            <Breadcrumb>
              <BreadcrumbItem to="/">主页</BreadcrumbItem>
              <BreadcrumbItem to="/Home">Components</BreadcrumbItem>
            </Breadcrumb>
          </div>
        </div>
        <div class="header-avator-con">
          <message-tip v-model="mesCount"></message-tip>
          <div class="user-dropdown-menu-con">
            <Row type="flex" justify="end" align="middle" class="user-dropdown-innercon">
              <Dropdown transfer trigger="click" @on-click="handleClickUserDropdown">
                <a href="javascript:void(0)">
                  <span class="main-user-name" v-text="user.username"></span>
                  <Icon type="arrow-down-b"></Icon>
                </a>
                <DropdownMenu slot="list">
                  <DropdownItem name="ownSpace">个人中心</DropdownItem>
                  <DropdownItem name="logout" divided >退出登录</DropdownItem>
                </DropdownMenu>
              </Dropdown>
              <Avatar :src="avator" style="margin-left: 10px;"></Avatar>
            </Row>
          </div>
        </div>
      </div>
    </div>
    <div class="single-page-con" :style="{left: '200px'}">
      <div class="single-page">
        <transition mode="out-in">
          <keep-alive>
            <router-view></router-view>
          </keep-alive>
        </transition>
      </div>
    </div>
  </div>

</template>

<script>
import messageTip from './custom-components/message-tip.vue'
import avator from '../assets/logo.png'
export default {
  name: 'Main',
  components: {
    messageTip
  },
  data () {
    return {
      mesCount: 1
    }
  },
  computed: {
    user () {
      return this.$store.state.UserInfo.user
    },
    avator () {
      return avator
    }
  },
  methods: {
    onMenuSelect: function (name) {
      this.$router.push(name)

      console.log(name, ' is clicked!')
    },
    handleClickUserDropdown: function (name) {
      if (name === 'logout') {
        this.$store.commit('logout')
        this.$router.go()
      }
      console.log(name, ' is clicked')
    }
  },
  updated () {
    this.$nextTick(() => {
      this.$refs.side_menu.updateActiveName()
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
