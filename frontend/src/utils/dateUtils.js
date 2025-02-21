// Helper function to convert GMT to IST
const convertGMTtoIST = (date) => {
  const istOffset = 5.5 * 60 * 60 * 1000 // IST is GMT+5:30
  return new Date(date.getTime() + istOffset)
}

export const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  
  // Format in both GMT and IST
  const gmtString = date.toLocaleString('en-US', {
    timeZone: 'GMT',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
  
  const istDate = convertGMTtoIST(date)
  const istString = istDate.toLocaleString('en-US', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
  
  return `${gmtString} GMT (${istString} IST)`
}

export const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  
  // Format in both GMT and IST
  const gmtString = date.toLocaleDateString('en-US', {
    timeZone: 'GMT',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
  
  const istDate = convertGMTtoIST(date)
  const istString = istDate.toLocaleDateString('en-US', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
  
  return `${gmtString} GMT (${istString} IST)`
}

export const formatTimeAgo = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diffMinutes = Math.round((now - date) / (1000 * 60))
  
  if (diffMinutes < 1) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes} minutes ago`
  if (diffMinutes < 120) return '1 hour ago'
  if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)} hours ago`
  if (diffMinutes < 2880) return 'yesterday'
  
  return formatDateTime(timestamp)
}

export const formatQuizDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  
  // Format in both GMT and IST
  const gmtString = date.toLocaleString('en-US', {
    timeZone: 'GMT',
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
  
  const istDate = convertGMTtoIST(date)
  const istString = istDate.toLocaleString('en-US', {
    timeZone: 'Asia/Kolkata',
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
  
  return `${gmtString} GMT (${istString} IST)`
} 