export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(access, refresh) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function removeToken() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

export function getUser() {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

export function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user))
}

export function isAuthenticated() {
  return !!getToken()
}
