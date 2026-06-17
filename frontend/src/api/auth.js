import request from '@/utils/request'

export function register(data) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data
  })
}

export function login(data) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

export function refreshToken(refresh) {
  return request({
    url: '/auth/refresh/',
    method: 'post',
    data: { refresh }
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/user/',
    method: 'get'
  })
}
