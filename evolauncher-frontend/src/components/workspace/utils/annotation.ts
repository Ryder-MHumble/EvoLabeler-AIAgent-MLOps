/**
 * 标注工具函数
 */

import type { BoundingBox } from '@/api/types'
import { CONFIDENCE_COLORS, CONFIDENCE_THRESHOLDS, LABEL_OPTIONS } from '../constants/annotation'

/**
 * 获取置信度颜色
 */
export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= CONFIDENCE_THRESHOLDS.HIGH) return CONFIDENCE_COLORS.HIGH
  if (confidence >= CONFIDENCE_THRESHOLDS.MEDIUM) return CONFIDENCE_COLORS.MEDIUM
  return CONFIDENCE_COLORS.LOW
}

/**
 * 限制数值在范围内
 */
export const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value))
}

/**
 * 下载文件
 */
export const downloadFile = (content: string, filename: string, mimeType: string): void => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * 导出 YOLO 格式标注
 */
export const exportYOLOFormat = (
  bboxes: BoundingBox[],
  imageId: string
): { annotation: string; classes: string } => {
  // YOLO格式: class_id center_x center_y width height (归一化坐标)
  const lines = bboxes.map((bbox) => {
    const classId = LABEL_OPTIONS.indexOf(bbox.label || '其他')
    const centerX = bbox.x + bbox.width / 2
    const centerY = bbox.y + bbox.height / 2
    return `${classId >= 0 ? classId : LABEL_OPTIONS.length - 1} ${centerX.toFixed(6)} ${centerY.toFixed(6)} ${bbox.width.toFixed(6)} ${bbox.height.toFixed(6)}`
  })
  
  return {
    annotation: lines.join('\n'),
    classes: LABEL_OPTIONS.join('\n')
  }
}

/**
 * 导出 JSON 格式标注
 */
export const exportJSONFormat = (
  bboxes: BoundingBox[],
  imageId: string,
  imageWidth: number,
  imageHeight: number
): string => {
  const data = {
    image_id: imageId,
    image_width: imageWidth,
    image_height: imageHeight,
    annotations: bboxes.map((bbox) => ({
      id: bbox.id,
      label: bbox.label || '目标',
      confidence: bbox.confidence,
      status: bbox.status,
      bbox: {
        x: bbox.x,
        y: bbox.y,
        width: bbox.width,
        height: bbox.height
      },
      bbox_pixels: {
        x: Math.round(bbox.x * imageWidth),
        y: Math.round(bbox.y * imageHeight),
        width: Math.round(bbox.width * imageWidth),
        height: Math.round(bbox.height * imageHeight)
      }
    }))
  }
  
  return JSON.stringify(data, null, 2)
}

/**
 * 解析 YOLO 格式标注
 */
export const parseYOLOAnnotation = (content: string): BoundingBox[] => {
  const lines = content.trim().split('\n').filter(line => line.trim())
  const bboxes: BoundingBox[] = []
  
  lines.forEach((line, index) => {
    const parts = line.trim().split(/\s+/).map(Number)
    if (parts.length < 5) return
    
    const [classId, centerX, centerY, width, height] = parts
    const x = centerX - width / 2
    const y = centerY - height / 2
    
    bboxes.push({
      id: `bbox-imported-${Date.now()}-${index}`,
      x: clamp(x, 0, 1),
      y: clamp(y, 0, 1),
      width: clamp(width, 0, 1),
      height: clamp(height, 0, 1),
      confidence: 1.0,
      label: LABEL_OPTIONS[classId] || '其他',
      status: 'confirmed'
    })
  })
  
  return bboxes
}

/**
 * 解析 JSON 格式标注
 */
export const parseJSONAnnotation = (content: string): BoundingBox[] => {
  try {
    const data = JSON.parse(content)
    let annotations = []
    
    // 支持多种 JSON 格式
    if (Array.isArray(data)) {
      annotations = data
    } else if (data.annotations && Array.isArray(data.annotations)) {
      annotations = data.annotations
    } else if (data.shapes && Array.isArray(data.shapes)) {
      annotations = data.shapes // LabelMe 格式
    }
    
    return annotations.map((anno: any, index: number) => {
      let bbox: BoundingBox = {
        id: anno.id || `bbox-imported-${Date.now()}-${index}`,
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        confidence: anno.confidence || 1.0,
        label: anno.label || '目标',
        status: (anno.status || 'confirmed') as 'pending' | 'confirmed'
      }
      
      // 处理不同的坐标格式
      if (anno.bbox) {
        bbox.x = anno.bbox.x
        bbox.y = anno.bbox.y
        bbox.width = anno.bbox.width
        bbox.height = anno.bbox.height
      } else if (anno.points && Array.isArray(anno.points) && anno.points.length === 2) {
        // LabelMe 格式 [[x1,y1], [x2,y2]]
        const [[x1, y1], [x2, y2]] = anno.points
        bbox.x = Math.min(x1, x2)
        bbox.y = Math.min(y1, y2)
        bbox.width = Math.abs(x2 - x1)
        bbox.height = Math.abs(y2 - y1)
      }
      
      return bbox
    })
  } catch (error) {
    console.error('解析 JSON 标注失败:', error)
    return []
  }
}

