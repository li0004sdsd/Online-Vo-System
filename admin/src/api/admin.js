import request from '@/utils/request'

export function getDashboardStats() {
  return request({
    url: '/admin/dashboard/',
    method: 'get'
  })
}

export function getPollList(status) {
  const params = status ? { status } : {}
  return request({
    url: '/admin/polls/',
    method: 'get',
    params
  })
}

export function getPollDetail(pollId) {
  return request({
    url: `/admin/polls/${pollId}/`,
    method: 'get'
  })
}

export function approvePoll(pollId) {
  return request({
    url: `/admin/polls/${pollId}/approve/`,
    method: 'post'
  })
}

export function rejectPoll(pollId, reason) {
  return request({
    url: `/admin/polls/${pollId}/reject/`,
    method: 'post',
    data: { reason }
  })
}
