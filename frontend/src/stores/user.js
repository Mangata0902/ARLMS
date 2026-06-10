import { defineStore } from 'pinia'
import { authAPI } from '../api/index.js'

export const useUserStore = defineStore('user', {
  state: () => ({ userInfo: null }),
  actions: {
    async fetchMe() {
      const res = await authAPI.me()
      this.userInfo = res.data
    },
    logout() {
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})
