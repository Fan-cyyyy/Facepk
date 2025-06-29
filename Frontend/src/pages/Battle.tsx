import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Typography, Avatar, Spin, message, Progress, Row, Col, Divider, Upload, Modal, Image } from 'antd';
import { UserOutlined, TrophyOutlined, FireOutlined, TeamOutlined, RocketOutlined, UploadOutlined, CameraOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../redux/store';
import { uploadAndScore } from '../services/api';
import { createMatch } from '../services/api';
import { useLocation, useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

interface UserData {
  user_id: number;
  username: string;
  avatar_url?: string;
}

interface BattleUser {
  id: number;
  username: string;
  avatar?: string;
  score: number;
  image_url: string;
  rank: number;
  score_id: number;
  beauty?: number;
}

const Battle: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const location = useLocation();
  
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [opponent, setOpponent] = useState<BattleUser | null>(null);
  const [battleResult, setBattleResult] = useState<'win' | 'lose' | 'draw' | null>(null);
  const [battleInProgress, setBattleInProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  
  // 照片上传相关状态
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [userScore, setUserScore] = useState<any | null>(null);
  
  // 摄像头相关状态
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  
  // 监听对手信息变化
  useEffect(() => {
    if (opponent) {
      console.log('对手信息已更新:', opponent);
    }
  }, [opponent]);
  
  // 从路由参数中获取对手信息
  useEffect(() => {
    // 检查location.state中是否包含对手信息
    if (location.state && location.state.opponent) {
      const opponentData = location.state.opponent;
      console.log('从路由获取的对手信息:', opponentData);
      setOpponent(opponentData);
    }
  }, [location]);
  
  // 模拟搜索对手 - 从排行榜选择一名用户作为对手
  const searchOpponent = async () => {
    if (!user) {
      message.error('请先登录');
      return;
    }
    
    setSearching(true);
    
    try {
      // 这里需要替换为实际API调用获取排行榜用户
      // 模拟获取一名排行榜用户
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockOpponent: BattleUser = {
        id: 2,
        username: `排行榜用户`,
        avatar: `/uploads/1_02ab9c6c-702a-4336-b4ea-55e60dbc7398.jpg`,
        score: 85.5,
        image_url: `/uploads/1_02ab9c6c-702a-4336-b4ea-55e60dbc7398.jpg`,
        rank: 1,
        score_id: 1
      };
      
      setOpponent(mockOpponent);
      message.success('已找到对手');
    } catch (error) {
      console.error('搜索对手失败:', error);
      message.error('搜索对手失败，请重试');
    } finally {
      setSearching(false);
    }
  };
  
  // 打开上传模态框
  const openUploadModal = () => {
    setShowUploadModal(true);
  };
  
  // 取消上传
  const cancelUpload = () => {
    setShowUploadModal(false);
    setImageFile(null);
    setPreviewImage(null);
    stopCamera();
  };
  
  // 处理文件选择
  const handleFileSelect = (info: any) => {
    // 这里只是为了接口完整性，实际上传在beforeUpload中处理
    console.log('文件选择:', info);
  };
  
  // 打开摄像头
  const openCamera = async () => {
    try {
      setShowCamera(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setCameraStream(stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('无法访问摄像头:', error);
      message.error('无法访问摄像头，请确保已授予权限');
      setShowCamera(false);
    }
  };
  
  // 关闭摄像头
  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setShowCamera(false);
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
            setPreviewImage(previewUrl);
            
            // 关闭摄像头
            stopCamera();
            
            message.success('照片拍摄成功');
          }
        }, 'image/jpeg', 0.95);
      }
    }
  };
  
  // 上传照片并开始PK
  const uploadAndStartBattle = async () => {
    if (!imageFile) {
      message.error('请先选择照片');
      return;
    }
    
    setLoading(true);
    
    try {
      // 上传照片并获取评分
      console.log('开始上传照片:', imageFile);
      const scoreResult = await uploadAndScore(imageFile, true);
      console.log('评分结果:', scoreResult);
      
      if (!scoreResult.success) {
        message.error(scoreResult.error || '上传评分失败');
        setLoading(false);
        return;
      }
      
      // 确保评分结果包含必要的字段
      const userScoreData = {
        ...scoreResult,
        face_score: scoreResult.face_score || 0,
        image_url: scoreResult.image_url || '',
        beauty: scoreResult.feature_highlights?.beauty || 0
      };
      
      setUserScore(userScoreData);
      setShowUploadModal(false);
      
      if (!opponent) {
        message.error('请先搜索对手');
        setLoading(false);
        return;
      }
      
      // 开始PK对战
      setBattleInProgress(true);
      setProgress(0);
      
      // 模拟PK进度
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 300);
      
      // 创建对战记录
      try {
        // 确保使用正确的score_id，这是上传照片后返回的评分ID
        const scoreId = scoreResult.score_id;
        
        if (!scoreId) {
          message.error('无法获取评分ID');
          clearInterval(interval);
          setBattleInProgress(false);
          setLoading(false);
          return;
        }
        
        console.log('创建对战，对手ID:', opponent.id, '评分ID:', scoreId);
        const matchResult = await createMatch(opponent.id, scoreId);
        console.log('对战结果:', matchResult);
        
        setTimeout(() => {
          clearInterval(interval);
          setProgress(100);
          
          if (matchResult.success) {
            // 输出对战结果中的对手信息
            console.log('对战结果中的对手信息:', matchResult.opponent);
            
            // 根据返回的结果设置对战结果
            if (matchResult.result === 'Win') {
              setBattleResult('win');
              console.log('对战胜利 - 我的分数:', userScoreData.face_score, '对手分数:', opponent.score);
            } else if (matchResult.result === 'Lose') {
              setBattleResult('lose');
              console.log('对战失败 - 我的分数:', userScoreData.face_score, '对手分数:', opponent.score);
            } else if (matchResult.result === 'Tie') {
              setBattleResult('draw');
              console.log('对战平局 - 我的分数:', userScoreData.face_score, '对手分数:', opponent.score);
            }
            
            // 更新对手信息，包括beauty值
            if (matchResult.opponent && matchResult.opponent.beauty !== undefined) {
              console.log('更新对手beauty值:', matchResult.opponent.beauty);
              // 使用函数式更新，确保获取最新的state
              setOpponent(prevOpponent => {
                if (!prevOpponent) return matchResult.opponent;
                return {
                  ...prevOpponent,
                  beauty: matchResult.opponent.beauty
                };
              });
            }
            
            // 更新用户排名信息
            if (userScore) {
              setUserScore({
                ...userScore,
                rank: matchResult.new_rating ? matchResult.new_rating : userScore.rank
              });
            }
          } else {
            message.error(matchResult.error || 'PK失败');
          }
          
          setTimeout(() => {
            setBattleInProgress(false);
          }, 1000);
        }, 2000);
        
      } catch (error) {
        clearInterval(interval);
        console.error('PK对战失败:', error);
        message.error('PK对战失败，请重试');
        setBattleInProgress(false);
      }
    } catch (error) {
      console.error('上传失败:', error);
      message.error('上传失败，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  // 重置PK
  const resetBattle = () => {
    setOpponent(null);
    setBattleResult(null);
    setBattleInProgress(false);
    setProgress(0);
    setUserScore(null);
  };
  
  // 查看排行榜
  const viewRankings = () => {
    navigate('/rankings');
  };
  
  // 显示对战结果
  const renderBattleResult = () => {
    if (!battleResult || !userScore || !opponent) return null;
    
    // 获取双方分数，保留两位小数
    const myScore = parseFloat(userScore.face_score).toFixed(1);
    const opponentScore = parseFloat(opponent.score).toFixed(1);
    
    // 获取beauty值
    const myBeauty = userScore.beauty !== undefined ? parseFloat(userScore.beauty).toFixed(1) : '未知';
    const opponentBeauty = opponent.beauty !== undefined ? parseFloat(opponent.beauty).toFixed(1) : '未知';
    
    console.log('渲染对战结果，对手beauty值:', opponent.beauty, '格式化后:', opponentBeauty);
    
    return (
      <div className="my-4 text-center">
        <div className={`p-4 rounded-lg ${
          battleResult === 'win' ? 'bg-green-50 text-green-600' : 
          battleResult === 'lose' ? 'bg-red-50 text-red-600' : 
          'bg-yellow-50 text-yellow-600'
        }`}>
          <Title level={3}>
            {battleResult === 'win' ? '恭喜，你赢了！' : 
             battleResult === 'lose' ? '很遗憾，你输了！' : 
             '平局！'}
          </Title>
          <p>
            {battleResult === 'win' ? `你的颜值评分(${myScore})高于对手(${opponentScore})！` : 
             battleResult === 'lose' ? `对手的颜值评分(${opponentScore})高于你(${myScore})！` : 
             `你们的颜值评分相同(${myScore})！`}
          </p>
          <p className="mt-2">
            <small>
              百度AI Beauty值: 你({myBeauty}) vs 对手({opponentBeauty})
              <br/>
              <span className="text-gray-500">*实际对战结果基于Beauty值判定</span>
            </small>
          </p>
        </div>
      </div>
    );
  };
  
  return (
    <div className="container mx-auto py-8 px-4">
      <Title level={2} className="text-center mb-6">颜值PK对战</Title>
      <Paragraph className="text-center mb-8 text-gray-500">
        与其他用户进行颜值PK对战，看看谁的颜值更胜一筹
      </Paragraph>
      
      <Card className="shadow-md mb-6">
        <div className="text-center mb-6">
          <Title level={4}>
            <FireOutlined className="mr-2 text-red-500" />
            开始一场PK对战
          </Title>
          <Paragraph className="text-gray-500">
            上传您的照片，与排行榜用户PK，赢取积分提升排名
          </Paragraph>
        </div>
        
        {!opponent ? (
          <div className="text-center py-8">
            <Button
              type="primary"
              size="large"
              icon={<TeamOutlined />}
              loading={searching}
              onClick={viewRankings}
              className="mb-4"
            >
              寻找对手
            </Button>
          </div>
        ) : (
          <>
            <Row gutter={24} className="items-center">
              <Col xs={24} sm={10} className="text-center">
                {userScore ? (
                  <>
                    <Image 
                      width={150}
                      height={150}
                      style={{ objectFit: 'cover', borderRadius: '50%' }}
                      src={userScore.image_url ? (userScore.image_url.startsWith('http') ? userScore.image_url : `http://localhost:8000${userScore.image_url}`) : ''}
                      fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJ5hVqKIwAAAABJRU5ErkJggg=="
                    />
                    <div className="mt-2">
                      <Title level={5}>评分: {userScore.face_score}</Title>
                      {userScore.beauty !== undefined && (
                        <p className="text-sm">Beauty: {userScore.beauty}</p>
                      )}
                      {userScore.feature_highlights && (
                        <div className="mt-2 text-sm text-left">
                          <p>年龄: {userScore.feature_highlights.age}</p>
                          <p>性别: {userScore.feature_highlights.gender === 'male' ? '男' : '女'}</p>
                          <p>脸型: {userScore.feature_highlights.face_shape}</p>
                          <p>表情: {userScore.feature_highlights.expression}</p>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <Button
                      type="primary"
                      size="large"
                      icon={<UploadOutlined />}
                      onClick={openUploadModal}
                      className="mb-4"
                    >
                      上传照片
                    </Button>
                  </div>
                )}
              </Col>
              <Col xs={24} sm={14}>
                {opponent && (
                  <div className="text-center py-8">
                    <Title level={4}>对手: {opponent.username}</Title>
                    <Image 
                      width={150}
                      height={150}
                      style={{ objectFit: 'cover', borderRadius: '50%' }}
                      src={opponent.image_url.startsWith('http') ? opponent.image_url : `http://localhost:8000${opponent.image_url}`}
                      fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJ5hVqKIwAAAABJRU5ErkJggg=="
                    />
                    <div className="mt-2">
                      <Title level={5}>对手评分: {opponent.score}</Title>
                      {opponent.beauty !== undefined && (
                        <p className="text-sm">Beauty: {opponent.beauty}</p>
                      )}
                      <Title level={5}>对手排名: {opponent.rank}</Title>
                    </div>
                  </div>
                )}
              </Col>
            </Row>
            
            {/* PK进度和结果 */}
            {battleInProgress && (
              <div className="my-4 text-center">
                <Progress percent={progress} status="active" />
                <p className="mt-2">PK对战进行中，请稍候...</p>
              </div>
            )}
            
            {battleResult && renderBattleResult()}
            
            <Divider />
            <div className="text-center py-8">
              <Button
                type="primary"
                size="large"
                icon={<RocketOutlined />}
                loading={loading}
                onClick={uploadAndStartBattle}
                className="mr-4"
                disabled={!userScore}
              >
                {loading ? 'PK中...' : '开始PK'}
              </Button>
              <Button
                type="default"
                size="large"
                icon={<UploadOutlined />}
                onClick={openUploadModal}
                className="mr-4"
              >
                重新上传
              </Button>
              <Button
                type="default"
                size="large"
                icon={<TeamOutlined />}
                onClick={resetBattle}
                className="mr-4"
              >
                重置PK
              </Button>
              <Button
                type="default"
                size="large"
                icon={<TrophyOutlined />}
                onClick={viewRankings}
              >
                查看排行榜
              </Button>
            </div>
          </>
        )}
      </Card>
      
      {/* 上传照片模态框 */}
      <Modal
        title="上传照片"
        open={showUploadModal}
        onCancel={cancelUpload}
        footer={[
          <Button key="cancel" onClick={cancelUpload}>
            取消
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            loading={loading}
            disabled={!imageFile}
            onClick={uploadAndStartBattle}
          >
            上传并开始PK
          </Button>,
        ]}
        width={600}
      >
        {showCamera ? (
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
        ) : (
          <>
            <div className="mb-4 text-center">
              <Button 
                type="primary" 
                icon={<CameraOutlined />} 
                onClick={openCamera}
                className="mb-4"
                size="large"
              >
                使用摄像头
              </Button>
              <p className="text-gray-500 mb-4">或者</p>
            </div>
            
            <Dragger
              name="file"
              multiple={false}
              showUploadList={false}
              beforeUpload={(file) => {
                setImageFile(file);
                // 创建预览
                const reader = new FileReader();
                reader.onload = () => {
                  setPreviewImage(reader.result as string);
                };
                reader.readAsDataURL(file);
                return false; // 阻止自动上传
              }}
              onChange={handleFileSelect}
              accept="image/jpeg,image/png,image/jpg"
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽照片到此区域上传</p>
              <p className="ant-upload-hint">
                支持单张图片上传，请选择清晰的正面照片
              </p>
            </Dragger>
            
            {previewImage && (
              <div className="mt-4 text-center">
                <h4>预览</h4>
                <div className="flex justify-center">
                  <Image
                    src={previewImage}
                    alt="预览"
                    style={{ 
                      maxWidth: '200px', 
                      maxHeight: '200px', 
                      borderRadius: '50%',
                      objectFit: 'cover'
                    }}
                  />
                </div>
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  );
};

export default Battle;