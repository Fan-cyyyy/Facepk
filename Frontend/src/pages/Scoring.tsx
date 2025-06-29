import React, { useState } from 'react';
import { Upload, Button, Card, Typography, Rate, Progress, Spin, message, Row, Col, Divider } from 'antd';
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

  // 拍照功能
  const handleCapture = () => {
    // 实际项目中应该调用摄像头API
    message.info('摄像头功能开发中...');
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
                  className="max-w-full h-auto mx-auto rounded-lg shadow-sm"
                  style={{ maxHeight: '300px' }}
                />
                <div className="mt-4">
                  <Button 
                    onClick={() => setImageUrl(null)} 
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
            
            <div className="flex justify-center space-x-4">
              {!imageUrl && (
                <>
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
                    <Button icon={<UploadOutlined />} size="large">
                      选择照片
                    </Button>
                  </Upload>
                  
                  <Button 
                    icon={<CameraOutlined />} 
                    size="large"
                    onClick={handleCapture}
                  >
                    拍照
                  </Button>
                </>
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
    </div>
  );
};

export default Scoring; 