import request from '@/utils/request'

export function getPollList() {
  return request({
    url: '/polls/',
    method: 'get'
  })
}

export function getPollDetail(id) {
  return request({
    url: `/polls/${id}/`,
    method: 'get'
  })
}

export function createPoll(data) {
  return request({
    url: '/polls/',
    method: 'post',
    data
  })
}

export function vote(pollId, optionIds) {
  return request({
    url: `/polls/${pollId}/vote/`,
    method: 'post',
    data: { option_ids: optionIds }
  })
}

export function getPollResults(id) {
  return request({
    url: `/polls/${id}/results/`,
    method: 'get'
  })
}

export function getUserVotes(pollId) {
  return request({
    url: `/polls/${pollId}/vote/`,
    method: 'get'
  })
}
