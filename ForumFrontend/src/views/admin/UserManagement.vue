<template>
  <div class="user-management-container">
    <el-card class="user-management-card">
      <template #header>
        <div class="clearfix">
          <span>用户管理</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名或邮箱"
            style="width: 300px; float: right"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #append>
              <el-button icon="el-icon-search" @click="handleSearch"></el-button>
            </template>
          </el-input>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else>
        <el-table
          :data="users"
          style="width: 100%"
          border
        >
          <el-table-column
            prop="id"
            label="ID"
            width="80"
            align="center"
          >
          </el-table-column>

          <el-table-column
            prop="username"
            label="用户名"
            width="120"
          >
          </el-table-column>

          <el-table-column
            prop="nickname"
            label="昵称"
            width="120"
          >
            <template #default="scope">
              {{ scope.row.nickname || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="email"
            label="邮箱"
            width="180"
          >
          </el-table-column>

          <el-table-column
            prop="role"
            label="角色"
            width="100"
            align="center"
          >
            <template #default="scope">
              <el-tag
                :type="getRoleTagType(scope.row.role)"
              >
                {{ getRoleLabel(scope.row.role) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="created_at"
            label="注册时间"
            width="180"
          >
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column
            prop="last_login"
            label="最后登录"
            width="180"
          >
            <template #default="scope">
              {{ scope.row.last_login ? formatDate(scope.row.last_login) : '-' }}
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            align="center"
          >
            <template #default="scope">
              <el-button
                size="small"
                type="primary"
                @click="handleViewUser(scope.row)"
              >
                查看
              </el-button>
              <el-button
                size="small"
                type="success"
                @click="handleEditUser(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="warning"
                @click="handleChangeRole(scope.row)"
              >
                角色
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteUser(scope.row)"
                :disabled="scope.row.id === currentUserId"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            :current-page="currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          >
          </el-pagination>
        </div>
      </div>
    </el-card>

    <!-- 编辑用户对话框 -->
    <el-dialog
      title="编辑用户信息"
      :visible="editDialogVisible"
      width="500px"
    >
      <el-form
        ref="userForm"
        :model="userForm"
        :rules="userRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" disabled></el-input>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" disabled></el-input>
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname"></el-input>
        </el-form-item>

        <el-form-item label="头像URL" prop="avatar_url">
          <el-input v-model="userForm.avatar_url"></el-input>
          <div class="avatar-preview">
            <el-avatar :size="60" :src="userForm.avatar_url || ''">
              {{ userForm.nickname?.charAt(0) || userForm.username?.charAt(0) || 'U' }}
            </el-avatar>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitUserForm" :loading="submitting">确 定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 修改角色对话框 -->
    <el-dialog
      title="修改用户角色"
      :visible="roleDialogVisible"
      width="400px"
    >
      <el-form
        ref="roleForm"
        :model="roleForm"
        label-width="80px"
      >
        <el-form-item label="用户名">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>

        <el-form-item label="当前角色">
          <el-tag :type="getRoleTagType(currentUser?.role)">
            {{ getRoleLabel(currentUser?.role) }}
          </el-tag>
        </el-form-item>

        <el-form-item label="新角色" prop="role">
          <el-select v-model="roleForm.role" placeholder="请选择角色">
            <el-option
              v-for="item in roleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitRoleForm" :loading="submitting">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/index'

// 格式化日期函数
const formatDate = (date) => {
  return formatDateTime(date)
}

export default {
  name: 'UserManagement',
  setup() {
    const router = useRouter()
    const store = useStore()

    // 状态
    const loading = ref(false)
    const users = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const searchQuery = ref('')

    // 当前用户ID
    const currentUserId = computed(() => store.getters.userInfo?.id)

    // 编辑用户对话框
    const editDialogVisible = ref(false)
    const userForm = ref({
      id: null,
      username: '',
      email: '',
      nickname: '',
      avatar_url: ''
    })
    const userRules = {
      nickname: [
        { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
      ]
    }

    // 修改角色对话框
    const roleDialogVisible = ref(false)
    const currentUser = ref(null)
    const roleForm = ref({
      role: ''
    })
    const roleOptions = [
      { value: 'user', label: '普通用户' },
      { value: 'moderator', label: '版主' },
      { value: 'admin', label: '管理员' }
    ]

    const submitting = ref(false)

    // 获取用户列表
    const fetchUsers = async () => {
      loading.value = true
      try {
        // 这里应该调用实际的API
        // const response = await getUserList({
        //   page: currentPage.value,
        //   page_size: pageSize.value,
        //   search: searchQuery.value
        // })
        // if (response.code === 0) {
        //   users.value = response.data.results || []
        //   total.value = response.data.count || 0
        // } else {
        //   ElMessage.error(response.msg || '获取用户列表失败')
        //   users.value = []
        //   total.value = 0
        // }
        
        // 暂时使用空数组，等待后端API实现
        setTimeout(() => {
          users.value = []
          total.value = 0
          loading.value = false
          ElMessage.info('用户管理功能尚未实现，请等待后续更新')
        }, 500)
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表失败')
        users.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }

    // 处理搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchUsers()
    }

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchUsers()
    }

    // 处理每页条数变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchUsers()
    }

    // 查看用户
    const handleViewUser = (user) => {
      router.push({ name: 'UserProfile', params: { id: user.id } })
    }

    // 编辑用户
    const handleEditUser = (user) => {
      userForm.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        nickname: user.nickname || '',
        avatar_url: user.avatar_url || ''
      }
      editDialogVisible.value = true
    }

    // 提交用户表单
    const submitUserForm = async () => {
      submitting.value = true
      try {
        // 这里应该调用实际的API
        // const response = await updateUser(userForm.value.id, {
        //   nickname: userForm.value.nickname,
        //   avatar_url: userForm.value.avatar_url
        // })
        // if (response.code === 0) {
        //   ElMessage.success(response.msg || '用户信息更新成功')
        //   editDialogVisible.value = false
        //   fetchUsers()
        // } else {
        //   ElMessage.error(response.msg || '用户信息更新失败')
        // }
        
        // 暂时使用提示信息
        setTimeout(() => {
          ElMessage.info('用户编辑功能尚未实现，请等待后续更新')
          editDialogVisible.value = false
          submitting.value = false
        }, 500)
      } catch (error) {
        console.error('用户信息更新失败:', error)
        ElMessage.error('用户信息更新失败')
      } finally {
        submitting.value = false
      }
    }

    // 修改角色
    const handleChangeRole = (user) => {
      currentUser.value = user
      roleForm.value.role = user.role
      roleDialogVisible.value = true
    }

    // 提交角色表单
    const submitRoleForm = async () => {
      if (!currentUser.value) return

      submitting.value = true
      try {
        // 模拟API调用
        setTimeout(() => {
          const index = users.value.findIndex(u => u.id === currentUser.value.id)
          if (index !== -1) {
            users.value[index] = {
              ...users.value[index],
              role: roleForm.value.role
            }
          }

          ElMessage.success('用户角色更新成功')
          roleDialogVisible.value = false
          submitting.value = false
        }, 500)

        // 实际API调用
        // const response = await updateUserRole(currentUser.value.id, {
        //   role: roleForm.value.role
        // })
        // if (response.code === 0) {
        //   ElMessage.success(response.msg || '用户角色更新成功')
        //   roleDialogVisible.value = false
        //   fetchUsers()
        // } else {
        //   ElMessage.error(response.msg || '用户角色更新失败')
        // }
      } catch (error) {
        console.error('用户角色更新失败:', error)
        ElMessage.error('用户角色更新失败')
      } finally {
        submitting.value = false
      }
    }

    // 删除用户
    const handleDeleteUser = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？此操作不可逆！`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 模拟API调用
        setTimeout(() => {
          users.value = users.value.filter(u => u.id !== user.id)
          total.value = users.value.length

          ElMessage.success('用户删除成功')
        }, 500)

        // 实际API调用
        // const response = await deleteUser(user.id)
        // if (response.code === 0) {
        //   ElMessage.success(response.msg || '用户删除成功')
        //   fetchUsers()
        // } else {
        //   ElMessage.error(response.msg || '用户删除失败')
        // }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('用户删除失败:', error)
          ElMessage.error('用户删除失败')
        }
      }
    }

    // 获取角色标签类型
    const getRoleTagType = (role) => {
      switch (role) {
        case 'admin':
          return 'danger'
        case 'moderator':
          return 'warning'
        case 'user':
          return 'success'
        default:
          return 'info'
      }
    }

    // 获取角色标签文本
    const getRoleLabel = (role) => {
      switch (role) {
        case 'admin':
          return '管理员'
        case 'moderator':
          return '版主'
        case 'user':
          return '普通用户'
        default:
          return '未知'
      }
    }

    // 生命周期钩子
    onMounted(() => {
      fetchUsers()
    })

    return {
      loading,
      users,
      total,
      currentPage,
      pageSize,
      searchQuery,
      currentUserId,
      editDialogVisible,
      userForm,
      userRules,
      roleDialogVisible,
      currentUser,
      roleForm,
      roleOptions,
      submitting,
      formatDate,
      handleSearch,
      handleCurrentChange,
      handleSizeChange,
      handleViewUser,
      handleEditUser,
      submitUserForm,
      handleChangeRole,
      submitRoleForm,
      handleDeleteUser,
      getRoleTagType,
      getRoleLabel
    }
  }
}
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.user-management-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.avatar-preview {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}
</style>
