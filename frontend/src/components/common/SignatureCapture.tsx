import { useRef, useState, useCallback, useEffect } from 'react'
import { Box, Button, Typography } from '@mui/material'
import { Clear as ClearIcon, Check as CheckIcon } from '@mui/icons-material'
import { useTranslation } from '../../utils/I18nProvider'

interface SignatureData {
  image: string
  contentHash: string
  timestamp: string
}

export default function SignatureCapture({ onSave, onClear }: { onSave: (data: SignatureData) => void; onClear?: () => void }) {
  const { t } = useTranslation()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [hasDrawn, setHasDrawn] = useState(false)

  const getCanvasCoords = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0 }
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height

    let clientX: number
    let clientY: number

    if ('touches' in e) {
      clientX = e.touches[0].clientX
      clientY = e.touches[0].clientY
    } else {
      clientX = e.clientX
      clientY = e.clientY
    }

    return { x: (clientX - rect.left) * scaleX, y: (clientY - rect.top) * scaleY }
  }, [])

  const startDrawing = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault()
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const { x, y } = getCanvasCoords(e)
    ctx.beginPath()
    ctx.moveTo(x, y)
    setIsDrawing(true)
    setHasDrawn(true)
  }, [getCanvasCoords])

  const draw = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault()
    if (!isDrawing) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const { x, y } = getCanvasCoords(e)
    ctx.lineTo(x, y)
    ctx.strokeStyle = '#000'
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.stroke()
  }, [isDrawing, getCanvasCoords])

  const stopDrawing = useCallback(() => {
    setIsDrawing(false)
  }, [])

  const handleSave = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const image = canvas.toDataURL('image/png')
    const timestamp = new Date().toISOString()
    let hash = 0
    for (let i = 0; i < image.length; i++) {
      const char = image.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash |= 0
    }
    onSave({ image, contentHash: `hash-${Math.abs(hash)}`, timestamp })
  }

  const handleClear = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    setHasDrawn(false)
    onClear?.()
  }

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }, [])

  return (
    <Box>
      <Typography variant="body2" gutterBottom>
        {t('common.signature') || 'امضا'}
      </Typography>
      <canvas
        ref={canvasRef}
        width={300}
        height={120}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
        style={{ border: '1px solid #ccc', borderRadius: 4, touchAction: 'none', width: '100%', maxWidth: 300, backgroundColor: '#fff' }}
      />
      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
        <Button variant="outlined" startIcon={<ClearIcon />} onClick={handleClear} size="small">
          {t('app.clear') || 'پاک کردن'}
        </Button>
        <Button variant="contained" startIcon={<CheckIcon />} onClick={handleSave} size="small" disabled={!hasDrawn}>
          {t('app.confirm') || 'تایید'}
        </Button>
      </Box>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
        {t('signatures.limitations') || 'امضای رسمی نیست. فقط برای تأیید داخلی.'}
      </Typography>
    </Box>
  )
}
