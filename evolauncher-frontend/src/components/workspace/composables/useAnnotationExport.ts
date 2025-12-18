/**
 * 标注导出 Composable
 * 负责导出YOLO和JSON格式标注
 */

import { type Ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { downloadFile, exportYOLOFormat, exportJSONFormat } from '../utils/annotation'
import type { ImageTask } from '@/api/types'

export const useAnnotationExport = (
  currentImage: Ref<ImageTask | null>,
  baseImageSize: Ref<{ naturalWidth: number; naturalHeight: number }>
) => {
  /**
   * 导出标注
   */
  const exportAnnotations = async () => {
    if (!currentImage.value || currentImage.value.boundingBoxes.length === 0) {
      ElMessage.warning('没有可导出的标注数据')
      return
    }
    
    try {
      await ElMessageBox.confirm(
        '选择导出格式',
        '导出标注',
        {
          confirmButtonText: 'YOLO格式',
          cancelButtonText: 'JSON格式',
          distinguishCancelAndClose: true
        }
      )
      exportYOLO()
    } catch (action) {
      if (action === 'cancel') {
        exportJSON()
      }
    }
  }

  /**
   * 导出 YOLO 格式
   */
  const exportYOLO = () => {
    if (!currentImage.value) return
    
    const { annotation, classes } = exportYOLOFormat(
      currentImage.value.boundingBoxes,
      currentImage.value.id
    )
    
    downloadFile(annotation, `${currentImage.value.id}_annotations.txt`, 'text/plain')
    downloadFile(classes, 'classes.txt', 'text/plain')
    
    ElMessage.success('YOLO格式标注已导出')
  }

  /**
   * 导出 JSON 格式
   */
  const exportJSON = () => {
    if (!currentImage.value) return
    
    const content = exportJSONFormat(
      currentImage.value.boundingBoxes,
      currentImage.value.id,
      baseImageSize.value.naturalWidth,
      baseImageSize.value.naturalHeight
    )
    
    downloadFile(content, `${currentImage.value.id}_annotations.json`, 'application/json')
    
    ElMessage.success('JSON格式标注已导出')
  }

  /**
   * 确认所有标注
   */
  const confirmAllBBoxes = async (updateBBox: (imageId: string, bboxId: string, updates: any) => void) => {
    if (!currentImage.value) return
    
    try {
      await ElMessageBox.confirm(
        '确认将所有标注框标记为已确认？',
        '批量确认',
        { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
      )
      
      currentImage.value.boundingBoxes.forEach(bbox => {
        if (bbox.status === 'pending') {
          updateBBox(currentImage.value!.id, bbox.id, { status: 'confirmed' })
        }
      })
      
      ElMessage.success('所有标注已确认')
    } catch {
      // 用户取消
    }
  }

  return {
    exportAnnotations,
    confirmAllBBoxes
  }
}

