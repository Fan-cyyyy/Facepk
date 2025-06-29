import React, { useState, useRef } from 'react';
import { Upload, Button, Card, Typography, Rate, Progress, Spin, message, Row, Col, Divider, Modal, Image } from 'antd';
import { UploadOutlined, CameraOutlined, RocketOutlined, InboxOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../redux/store';
import { setCurrentScore, setUploadProgress } from '../redux/slices/scoreSlice';
import type { UploadProps } from 'antd';
import { uploadAndScore, ScoreDetail, ScoreResponse } from '../services/api';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

const Scoring: React.FC = () => {
  const dispatch = useDispatch();
  const { currentScore, uploadProgress, loading } = useSelector((state: RootState) => state.score);
  
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [scoreDetails, setScoreDetails] = useState<ScoreDetail[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  
  // 摄像头相关状态
  const [showCameraModal, setShowCameraModal] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // 处理上传图片
  const handleUpload = (info: any) => {
    console.log('上传状态:', info.file.status, info);
    
    if (info.file.status === 'uploading') {
      const percent = info.file.percent || 0;
      dispatch(setUploadProgress(percent));
      return;
    }
    
    if (info.file.status === 'done') {
      dispatch(setUploadProgress(100));
      
      // 获取上传的图片URL和文件对象
      if (info.file.originFileObj) {
        const url = URL.createObjectURL(info.file.originFileObj);
        setImageUrl(url);
        setImageFile(info.file.originFileObj); // 保存文件对象用于后续API调用
        message.success('图片上传成功');
      }
    } else if (info.file.status === 'error') {
      message.error('图片上传失败');
    }
  };

  // 自定义上传请求
  const customRequest = ({ file, onSuccess }: any) => {
    console.log('自定义上传请求:', file);
    
    // 模拟上传成功
    setTimeout(() => {
      if (onSuccess) {
        onSuccess("ok");
      }
    }, 500);
    
    return {
      abort() {
        console.log('上传终止');
      }
    };
  };

  // 分析照片
  const analyzePhoto = async () => {
    if (!imageFile) {
      message.error('请先上传照片');
      return;
    }
    
    setAnalyzing(true);
    
    try {
      // 调用实际的API
      const response: ScoreResponse = await uploadAndScore(imageFile, true);
      
      if (!response.success) {
        throw new Error(response.error || '评分失败');
      }
      
      // 保存评分结果
      const score = response.face_score || 0;
      const details = response.score_details || [];
      
      setScoreDetails(details);
      dispatch(setCurrentScore(score));
      
      message.success('分析完成');
    } catch (error) {
      console.error('分析失败:', error);
      message.error('分析失败，请重试');
    } finally {
      setAnalyzing(false);
    }
  };

  // 打开摄像头
  const openCamera = async () => {
    try {
      setShowCameraModal(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setCameraStream(stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('无法访问摄像头:', error);
      message.error('无法访问摄像头，请确保已授予权限');
      setShowCameraModal(false);
    }
  };
  
  // 关闭摄像头
  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setShowCameraModal(false);
  };
  
  // 拍照
  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // 获取视频尺寸
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;
      
      // 计算正方形裁剪区域（取最小边作为边长）
      const size = Math.min(videoWidth, videoHeight);
      const offsetX = (videoWidth - size) / 2;
      const offsetY = (videoHeight - size) / 2;
      
      // 设置canvas尺寸为正方形
      canvas.width = size;
      canvas.height = size;
      
      // 在canvas上绘制当前视频帧（裁剪为正方形）
      const context = canvas.getContext('2d');
      if (context) {
        // 清除画布
        context.clearRect(0, 0, size, size);
        
        // 创建圆形裁剪区域
        context.beginPath();
        context.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2, true);
        context.closePath();
        context.clip();
        
        // 绘制视频帧到圆形区域
        context.drawImage(
          video,
          offsetX, offsetY, size, size,  // 源图像的裁剪区域
          0, 0, size, size               // 目标区域
        );
        
        // 将canvas内容转换为图片
        canvas.toBlob((blob) => {
          if (blob) {
            // 创建File对象
            const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
            setImageFile(file);
            
            // 创建预览URL
            const previewUrl = URL.createObjectURL(blob);
            setImageUrl(previewUrl);
            
            // 关闭摄像头
            stopCamera();
            
            message.success('照片拍摄成功');
          }
        }, 'image/jpeg', 0.95);
      }
    }
  };

  // 拖拽上传配置
  const draggerProps: UploadProps = {
    name: 'file',
    multiple: false,
    maxCount: 1,
    accept: 'image/*',
    showUploadList: false,
    customRequest: customRequest,
    onChange: handleUpload,
    beforeUpload: (file) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('只能上传图片文件!');
        return false;
      }
      
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过2MB!');
        return false;
      }
      
      return true;
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <Title level={2} className="text-center mb-6">颜值评分</Title>
      <Paragraph className="text-center mb-8 text-gray-500">
        上传您的照片，AI将为您提供专业的颜值评分和建议
      </Paragraph>
      
      <Row gutter={24}>
        <Col xs={24} md={12}>
          <Card className="mb-6 shadow-md">
            <div className="text-center mb-4">
              <Title level={4}>上传照片</Title>
              <Paragraph className="text-gray-500">
                请上传正面、光线充足的照片以获得最准确的评分
              </Paragraph>
            </div>
            
            {imageUrl ? (
              <div className="mb-4 text-center">
                <img 
                  src={imageUrl} 
                  alt="上传的照片" 
                  className="max-w-full h-auto mx-auto rounded-full shadow-sm"
                  style={{ maxHeight: '300px', objectFit: 'cover' }}
                />
                <div className="mt-4">
                  <Button 
                    onClick={() => {
                      setImageUrl(null);
                      setImageFile(null);
                    }} 
                    size="small"
                  >
                    重新上传
                  </Button>
                </div>
              </div>
            ) : (
              <Dragger {...draggerProps} className="mb-4">
                <p className="ant-upload-drag-icon">
                  <InboxOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                </p>
                <p className="ant-upload-text">点击或拖拽照片到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个图片上传，大小不超过2MB
                </p>
              </Dragger>
            )}
            
            <div className="text-center mt-4">
              {!imageUrl && (
                <div className="space-x-4">
                  <Upload
                    name="avatar"
                    showUploadList={false}
                    customRequest={customRequest}
                    onChange={handleUpload}
                    accept="image/*"
                    beforeUpload={(file) => {
                      const isImage = file.type.startsWith('image/');
                      if (!isImage) {
                        message.error('只能上传图片文件!');
                        return false;
                      }
                      
                      const isLt2M = file.size / 1024 / 1024 < 2;
                      if (!isLt2M) {
                        message.error('图片大小不能超过2MB!');
                        return false;
                      }
                      
                      return true;
                    }}
                  >
                    <Button icon={<UploadOutlined />} size="large" className="mr-4">
                      选择照片
                    </Button>
                  </Upload>
                  
                  <Button 
                    icon={<CameraOutlined />} 
                    size="large"
                    onClick={openCamera}
                  >
                    拍照
                  </Button>
                </div>
              )}
            </div>
            
            {uploadProgress > 0 && uploadProgress < 100 && (
              <Progress percent={uploadProgress} className="mt-4" />
            )}
          </Card>
          
          <Button 
            type="primary" 
            size="large" 
            block 
            icon={<RocketOutlined />}
            onClick={analyzePhoto}
            loading={analyzing}
            disabled={!imageUrl}
          >
            开始分析
          </Button>
        </Col>
        
        <Col xs={24} md={12}>
          <Card className="shadow-md">
            <div className="text-center mb-4">
              <Title level={4}>评分结果</Title>
            </div>
            
            {analyzing ? (
              <div className="py-12 flex flex-col items-center">
                <Spin size="large" />
                <p className="mt-4 text-gray-500">AI正在分析您的照片...</p>
              </div>
            ) : currentScore ? (
              <>
                <div className="score-result mb-6">
                  <div className="score-number">{currentScore}</div>
                  <div className="score-label">综合颜值评分</div>
                </div>
                
                <Divider>详细评分</Divider>
                
                {scoreDetails.map((detail, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">{detail.category}</span>
                      <span>{detail.score}/10</span>
                    </div>
                    <Rate disabled defaultValue={detail.score} count={10} />
                    <p className="mt-1 text-sm text-gray-500">{detail.description}</p>
                  </div>
                ))}
              </>
            ) : (
              <div className="py-12 text-center text-gray-500">
                <p>请上传照片并点击"开始分析"按钮获取评分</p>
              </div>
            )}
          </Card>
        </Col>
      </Row>
      
      {/* 摄像头模态框 */}
      <Modal
        title="拍摄照片"
        open={showCameraModal}
        onCancel={stopCamera}
        footer={null}
        width={600}
      >
        <div className="text-center">
          <div className="mb-4 flex justify-center">
            <div 
              className="relative rounded-full overflow-hidden border-4 border-primary shadow-lg"
              style={{ 
                width: '350px', 
                height: '350px',
                background: '#f0f0f0'
              }}
            >
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                style={{ 
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
              <div 
                className="absolute inset-0 rounded-full"
                style={{ 
                  boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)',
                  border: '1px solid rgba(255,255,255,0.3)'
                }}
              ></div>
            </div>
          </div>
          <div className="mb-4">
            <Button 
              type="primary" 
              icon={<CameraOutlined />} 
              onClick={takePhoto}
              className="mr-2"
              size="large"
            >
              拍照
            </Button>
            <Button 
              onClick={stopCamera}
              size="large"
            >
              取消
            </Button>
          </div>
          {/* 隐藏的canvas用于拍照 */}
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
      </Modal>
    </div>
  );
};

export default Scoring; 