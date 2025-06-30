<template>
  <div class="complaints-container">
    <div class="page-header">
      <h1>投诉中心</h1>
      <p>如果您在使用过程中遇到问题或有任何建议，请在此提交</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <div class="complaint-form-container">
          <div class="form-header">
            <h2>提交投诉</h2>
          </div>

          <el-form
            ref="complaintFormRef"
            :model="complaintForm"
            :rules="rules"
            label-position="top"
            class="complaint-form"
          >
            <el-form-item label="投诉类型" prop="type">
              <el-select v-model="complaintForm.type" placeholder="请选择投诉类型" class="full-width">
                <el-option label="内容违规" value="content_violation" />
                <el-option label="用户行为" value="user_behavior" />
                <el-option label="系统问题" value="system_issue" />
                <el-option label="功能建议" value="feature_suggestion" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>

            <el-form-item label="标题" prop="title">
              <el-input v-model="complaintForm.title" placeholder="请简要描述您的投诉" />
            </el-form-item>

            <el-form-item label="详细描述" prop="content">
              <el-input
                v-model="complaintForm.content"
                type="textarea"
                :rows="6"
                placeholder="请详细描述您遇到的问题或建议"
              />
            </el-form-item>

            <el-form-item label="相关链接" prop="related_url">
              <el-input
                v-model="complaintForm.related_url"
                placeholder="如果有相关的帖子或页面链接，请在此提供"
              />
            </el-form-item>

            <el-form-item label="联系方式" prop="contact_info">
              <el-input
                v-model="complaintForm.contact_info"
                placeholder="请留下您的联系方式，以便我们回复您（选填）"
              />
            </el-form-item>

            <el-form-item label="上传附件" prop="attachments">
              <el-upload
                class="complaint-upload"
                action="#"
                :auto-upload="false"
                :limit="3"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :file-list="fileList"
              >
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持jpg、png、pdf格式，单个文件不超过5MB，最多上传3个文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="submitting"
                @click="submitComplaint"
              >
                提交投诉
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="complaint-info">
          <h3>投诉须知</h3>
          <div class="info-content">
            <p><strong>1. 投诉处理流程</strong></p>
            <p>我们会在收到您的投诉后的3个工作日内进行处理，并通过您提供的联系方式回复您。</p>
            
            <p><strong>2. 投诉类型说明</strong></p>
            <ul>
              <li><strong>内容违规：</strong>举报违反社区规定的内容，如色情、暴力、歧视等。</li>
              <li><strong>用户行为：</strong>举报用户的不当行为，如骚扰、威胁、欺诈等。</li>
              <li><strong>系统问题：</strong>报告系统故障或错误，如页面无法加载、功能失效等。</li>
              <li><strong>功能建议：</strong>提出对论坛功能的改进建议。</li>
              <li><strong>其他：</strong>不属于以上类型的投诉或建议。</li>
            </ul>
            
            <p><strong>3. 注意事项</strong></p>
            <ul>
              <li>请提供真实、准确的信息，以便我们更好地处理您的投诉。</li>
              <li>恶意投诉或提供虚假信息可能会导致您的账号被限制。</li>
              <li>如果您的投诉涉及紧急情况，请直接联系管理员。</li>
            </ul>
          </div>

          <div class="contact-info">
            <h3>联系我们</h3>
            <p>邮箱：support@forumexample.com</p>
            <p>工作时间：周一至周五 9:00-18:00</p>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog
      v-model="dialogVisible"
      title="投诉提交成功"
      width="30%"
      center
    >
      <div class="success-dialog">
        <el-icon class="success-icon"><circle-check /></el-icon>
        <p>您的投诉已成功提交，我们会尽快处理并回复您。</p>
        <p>投诉编号：{{ complaintId }}</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="goToHome">返回首页</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleCheck } from '@element-plus/icons-vue'

export default {
  name: 'Complaints',
  components: {
    CircleCheck
  },
  setup() {
    const router = useRouter()
    const complaintForm = reactive({
      type: '',
      title: '',
      content: '',
      related_url: '',
      contact_info: '',
      attachments: []
    })

    const fileList = ref([])
    const submitting = ref(false)
    const dialogVisible = ref(false)
    const complaintId = ref('')
    const complaintFormRef = ref(null)

    const rules = {
      type: [
        { required: true, message: '请选择投诉类型', trigger: 'change' }
      ],
      title: [
        { required: true, message: '请输入投诉标题', trigger: 'blur' },
        { min: 5, max: 100, message: '标题长度应在5到100个字符之间', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入详细描述', trigger: 'blur' },
        { min: 10, max: 1000, message: '描述长度应在10到1000个字符之间', trigger: 'blur' }
      ],
      related_url: [
        { pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w.-]*)*\/?$/, message: '请输入有效的URL', trigger: 'blur' }
      ]
    }

    const handleFileChange = (file) => {
      // 文件类型验证
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
      if (!allowedTypes.includes(file.raw.type)) {
        ElMessage.error('只支持JPG、PNG和PDF格式的文件')
        return false
      }
      
      // 文件大小验证（5MB）
      const isLt5M = file.size / 1024 / 1024 < 5
      if (!isLt5M) {
        ElMessage.error('文件大小不能超过5MB')
        return false
      }
      
      complaintForm.attachments.push(file.raw)
      return true
    }

    const handleFileRemove = (file) => {
      const index = complaintForm.attachments.findIndex(item => item.uid === file.uid)
      if (index !== -1) {
        complaintForm.attachments.splice(index, 1)
      }
    }

    const submitComplaint = () => {
      complaintFormRef.value.validate((valid) => {
        if (valid) {
          submitting.value = true
          
          // 模拟API调用
          setTimeout(() => {
            // 生成随机投诉编号
            complaintId.value = `CP${Date.now().toString().slice(-8)}${Math.floor(Math.random() * 1000)}`
            
            submitting.value = false
            dialogVisible.value = true
            
            // 在实际项目中，这里应该调用API提交投诉
            console.log('提交的投诉信息:', complaintForm)
          }, 1500)
        } else {
          ElMessage.error('请正确填写投诉表单')
          return false
        }
      })
    }

    const resetForm = () => {
      complaintFormRef.value.resetFields()
      fileList.value = []
      complaintForm.attachments = []
    }

    const goToHome = () => {
      dialogVisible.value = false
      router.push('/')
    }

    return {
      complaintForm,
      rules,
      fileList,
      submitting,
      dialogVisible,
      complaintId,
      complaintFormRef,
      handleFileChange,
      handleFileRemove,
      submitComplaint,
      resetForm,
      goToHome
    }
  }
}
</script>

<style scoped>
.complaints-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #606266;
  font-size: 16px;
}

.complaint-form-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.form-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.form-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.complaint-form {
  padding: 10px 0;
}

.full-width {
  width: 100%;
}

.complaint-upload {
  width: 100%;
}

.complaint-info {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  position: sticky;
  top: 80px;
}

.complaint-info h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.info-content {
  margin-bottom: 20px;
}

.info-content p {
  margin-bottom: 10px;
}

.info-content ul {
  padding-left: 20px;
  margin-bottom: 15px;
}

.info-content li {
  margin-bottom: 5px;
}

.contact-info {
  background-color: #f0f9ff;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
}

.contact-info h3 {
  margin-top: 0;
  border-bottom: none;
  padding-bottom: 5px;
}

.contact-info p {
  margin: 5px 0;
  color: #606266;
}

.success-dialog {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 60px;
  color: #67c23a;
  margin-bottom: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style> 