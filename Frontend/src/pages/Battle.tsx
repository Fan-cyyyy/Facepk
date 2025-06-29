import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Avatar, Spin, message, Progress, Row, Col, Divider, Upload, Modal, Image } from 'antd';
import { UserOutlined, TrophyOutlined, FireOutlined, TeamOutlined, RocketOutlined, UploadOutlined } from '@ant-design/icons';
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
  
  // 从路由参数中获取对手信息
  useEffect(() => {
    // 检查location.state中是否包含对手信息
    if (location.state && location.state.opponent) {
      setOpponent(location.state.opponent);
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
  };
  
  // 处理文件选择
  const handleFileSelect = (info: any) => {
    if (info.file) {
      const file = info.file.originFileObj || info.file;
      setImageFile(file);
      
      // 创建预览
      const reader = new FileReader();
      reader.onload = () => {
        setPreviewImage(reader.result as string);
      };
      reader.readAsDataURL(file);
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
        image_url: scoreResult.image_url || ''
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
            // 根据返回的结果设置对战结果
            if (matchResult.result === 'Win') {
              setBattleResult('win');
            } else if (matchResult.result === 'Lose') {
              setBattleResult('lose');
            } else {
              setBattleResult('draw');
            }
            
            // 更新用户排名信息
            if (userScore) {
              setUserScore({
                ...userScore,
                rank: matchResult.new_rating ? matchResult.new_rating : userScore.rank
              });
            }
            
            // 3秒后导航到排行榜页面
            setTimeout(() => {
              message.success('PK完成，正在跳转到排行榜...');
              // 设置一个标志，表示需要刷新排行榜
              sessionStorage.setItem('refreshRankings', 'true');
              navigate('/rankings');
            }, 3000);
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
                      style={{ objectFit: 'cover' }}
                      src={userScore.image_url ? (userScore.image_url.startsWith('http') ? userScore.image_url : `http://localhost:8000${userScore.image_url}`) : ''}
                      fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJ5hVqKIwAAAABJRU5ErkJggg=="
                    />
                    <div className="mt-2">
                      <Title level={5}>评分: {userScore.face_score}</Title>
                      <Title level={5}>排名: {userScore.rank || '计算中'}</Title>
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
                      style={{ objectFit: 'cover' }}
                      src={opponent.image_url.startsWith('http') ? opponent.image_url : `http://localhost:8000${opponent.image_url}`}
                      fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAJ5hVqKIwAAAABJRU5ErkJggg=="
                    />
                    <div className="mt-2">
                      <Title level={5}>对手评分: {opponent.score}</Title>
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
            
            {battleResult && (
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
                    {battleResult === 'win' ? '你的颜值评分高于对手！' : 
                     battleResult === 'lose' ? '对手的颜值评分高于你！' : 
                     '你们的颜值评分相同！'}
                  </p>
                </div>
              </div>
            )}
            
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
      >
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
            <Image
              src={previewImage}
              alt="预览"
              style={{ maxWidth: '100%', maxHeight: '200px' }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Battle;