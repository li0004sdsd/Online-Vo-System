const TOKEN_KEY = 'admin_token'
const USER_KEY = 'admin_user'

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(token))
}

export function getToken() {
  const data = localStorage.getItem(TOKEN_KEY)
  return data ? JSON.parse(data) : null
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function setUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function getUser() {
  const data = localStorage.getItem(USER_KEY)
  return data ? JSON.parse(data) : null
}

export function isAdmin() {
  const user = getUser()
  return user && user.is_staff === true
}

export function getAccessToken() {
  const token = getToken()
  return token ? token.access : null
}
