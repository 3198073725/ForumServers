<template>
  <div class="change-password-container">
    <el-card class="password-card">
      <div slot="header" class="clearfix">
        <span>修改密码</span>
      </div>

      <el-form
        ref="passwordForm"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          ></el-input>
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          ></el-input>
        </el-form-item>

        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          ></el-input>
        </el-form-item>

        <el-form-item>
          <el-button @click="cancel">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确认修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/profile'

export default {
  name: 'ChangePassword',
  setup() {
    const router = useRouter()
    const store = useStore()
    const passwordForm = ref({
      old_password: '',
      new_password: '',
      confirm_password: ''
    })

    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== passwordForm.value.new_password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    const passwordRules = {
      old_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }

    const submitting = ref(false)

    const submitForm = async () => {
      const formEl = document.querySelector('.change-password-container .el-form')
      if (!formEl) return

      formEl.validate(async (valid) => {
        if (valid) {
          submitting.value = true
          try {
            const response = await changePassword(passwordForm.value)
            if (response.code === 0) {
              ElMessage.success(response.msg || '密码修改成功，请重新登录')

              // 退出登录
              store.dispatch('logout')
              router.push('/login')
            } else {
              ElMessage.error(response.msg || '密码修改失败')
            }
          } catch (error) {
            console.error('密码修改失败:', error)
            ElMessage.error('密码修改失败')
          } finally {
            submitting.value = false
          }
        } else {
          return false
        }
      })
    }

    const cancel = () => {
      // 使用router.back()返回上一页
      router.back()
    }

    return {
      passwordForm,
      passwordRules,
      submitting,
      submitForm,
      cancel
    }
  }
}
</script>

<style scoped>
.change-password-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.password-card {
  margin-bottom: 20px;
}
</style>
