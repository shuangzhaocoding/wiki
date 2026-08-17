<template>
  <div class="login-container">
    <AuthLocaleSwitcher />
    <div class="login-box">
      <h2 class="login-title">{{ translate('login.title') }}</h2>
      
      <tiny-form
        ref="loginFormRef"
        class="auth-form"
        :model="loginForm"
        :rules="rules"
        :label-position="formLabelPosition"
        :label-width="formLabelWidth"
        @submit.prevent="handleLogin"
      >
        <tiny-form-item :label="translate('login.email')" prop="email">
          <tiny-input
            v-model="loginForm.email"
            :placeholder="translate('login.email.placeholder')"
            clearable
            @keyup.enter="handleLogin"
          />
        </tiny-form-item>

        <tiny-form-item :label="translate('login.password')" prop="password">
          <tiny-input
            v-model="loginForm.password"
            type="password"
            :placeholder="translate('login.password.placeholder')"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </tiny-form-item>

        <tiny-form-item>
          <div class="login-helper">
            <router-link to="/forgot-password" class="forgot-link">{{ translate('login.forgotPassword') }}</router-link>
          </div>
        </tiny-form-item>

        <tiny-form-item>
          <tiny-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ translate('login.button') }}
          </tiny-button>
        </tiny-form-item>

        <tiny-form-item>
          <div class="login-footer">
            <span>{{ translate('login.noAccount') }}</span>
            <router-link to="/register" class="register-link">{{ translate('login.register') }}</router-link>
          </div>
        </tiny-form-item>
      </tiny-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Button as TinyButton, Modal } from '@opentiny/vue'
import { authApi } from '../api/auth'
import { authUtils } from '../utils/auth'
import { useUserStore } from '../stores/user'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import AuthLocaleSwitcher from '../components/AuthLocaleSwitcher.vue'
import { useAuthFormLayout } from '../composables/useAuthFormLayout'

const router = useRouter()
const { formLabelPosition, formLabelWidth } = useAuthFormLayout()
const route = useRoute()
const loginFormRef = ref()
const loading = ref(false)
const localeStore = useLocaleStore()
const userStore = useUserStore()

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const loginForm = reactive({
  email: '',
  password: ''
})

// 邮箱格式验证
const validateEmail = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) {
    callback(new Error(translate('login.email.required')))
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      callback(new Error(translate('login.email.invalid')))
    } else {
      callback()
    }
  }
}

const rules = computed(() => ({
  email: [
    { required: true, message: translate('login.email.required'), trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  password: [
    { required: true, message: translate('login.password.required'), trigger: 'blur' },
    { min: 6, message: translate('login.password.min'), trigger: 'blur' }
  ]
}))

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    loading.value = true
    try {
      const response = await authApi.login({
        username: loginForm.email,
        password: loginForm.password
      })
      
      // 保存 token
      authUtils.setToken(response.access_token, response.token_type)
      
      // 获取并存储用户信息
      await userStore.fetchCurrentUser()
      Modal.message({ message: translate('login.success'), status: 'success' })
      console.log('userStore.currentUserRoles------login', userStore.currentUserRoles)
      // 跳转到之前访问的页面，如果没有则跳转到首页
      const redirect = route.query.redirect as string
      console.log('redirect', redirect)
      if (redirect && redirect !== '/login') {
        router.push(redirect)
      } else {
        router.push('/')
      }
    } catch (error: any) {
      const errorMsg = error?.message || translate('login.failed')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="less">
@import '../styles/auth-page-shell.less';

.login-container {
  .auth-page-shell();
}

.login-box {
  .auth-page-card(400px);
  .auth-form-responsive();
}

.login-title {
  .auth-page-title();
}

.login-footer {
  .auth-page-footer();
}

.login-helper {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}

.forgot-link,
.register-link {
  .auth-page-link();
}

.register-link {
  margin-left: 5px;
}
</style>
