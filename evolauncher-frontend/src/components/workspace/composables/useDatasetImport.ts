/**
 * 数据集导入 Composable
 * 负责批量导入已标注数据集（YOLO/JSON格式）
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useMissionStore } from '@/store/mission'
import { parseYOLOAnnotation, parseJSONAnnotation } from '../utils/annotation'
import type { BoundingBox } from '@/api/types'

export const useDatasetImport = () => {
  const missionStore = useMissionStore()
  const datasetInputRef = ref<HTMLInputElement | null>(null)

  /**
   * 触发数据集导入
   */
  const triggerDatasetImport = () => {
    datasetInputRef.value?.click()
  }

  /**
   * 处理数据集导入
   */
  const handleDatasetImport = async (event: Event) => {
    const target = event.target as HTMLInputElement
    if (!target.files || target.files.length === 0) return
    
    const files = Array.from(target.files)
    const imageFiles = files.filter(f => f.type.startsWith('image/'))
    const annotationFiles = files.filter(f => 
      f.name.endsWith('.txt') || f.name.endsWith('.json')
    )
    
    if (imageFiles.length === 0) {
      ElMessage.warning('未找到图片文件')
      target.value = ''
      return
    }
    
    try {
      ElMessage.info(`正在导入 ${imageFiles.length} 张图片...`)
      
      for (const imageFile of imageFiles) {
        await processImageWithAnnotation(imageFile, annotationFiles)
      }
      
      ElMessage.success(`成功导入 ${imageFiles.length} 张图片`)
    } catch (error) {
      console.error('导入数据集失败:', error)
      ElMessage.error('导入数据集失败')
    }
    
    target.value = ''
  }

  /**
   * 处理单张图片及其标注
   */
  const processImageWithAnnotation = async (
    imageFile: File,
    annotationFiles: File[]
  ): Promise<void> => {
    return new Promise((resolve) => {
      const reader = new FileReader()
      
      reader.onload = async (e) => {
        const imageUrl = e.target?.result as string
        const imageId = imageFile.name.replace(/\.[^/.]+$/, '')
        
        // 查找对应的标注文件
        const annotationFile = annotationFiles.find(f => {
          const annoName = f.name.replace(/\.[^/.]+$/, '')
          return annoName === imageId
        })
        
        let boundingBoxes: BoundingBox[] = []
        
        if (annotationFile) {
          const annoReader = new FileReader()
          
          annoReader.onload = async (annoEvent) => {
            const content = annoEvent.target?.result as string
            
            if (annotationFile.name.endsWith('.txt')) {
              boundingBoxes = parseYOLOAnnotation(content)
            } else if (annotationFile.name.endsWith('.json')) {
              boundingBoxes = parseJSONAnnotation(content)
            }
            
            await addToStream(imageId, imageUrl, boundingBoxes)
            resolve()
          }
          
          annoReader.readAsText(annotationFile)
        } else {
          await addToStream(imageId, imageUrl, [])
          resolve()
        }
      }
      
      reader.readAsDataURL(imageFile)
    })
  }

  /**
   * 添加到数据流
   */
  const addToStream = async (
    imageId: string,
    imageUrl: string,
    boundingBoxes: BoundingBox[]
  ) => {
    await missionStore.addImageToStream({
      id: `imported-${Date.now()}-${imageId}`,
      url: imageUrl,
      thumbnailUrl: imageUrl,
      confidence: 1.0,
      source: 'manual',
      boundingBoxes,
      createdAt: new Date().toISOString(),
      status: 'incoming'
    })
  }

  return {
    datasetInputRef,
    triggerDatasetImport,
    handleDatasetImport
  }
}

