import React, { useEffect } from 'react';
import { Typography, Button, Card, Row, Col } from 'antd';
import { Link } from 'react-router-dom';
import { CameraOutlined, ThunderboltOutlined, TrophyOutlined, UserOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  // 添加调试日志
  useEffect(() => {
    console.log('Home组件渲染，认证状态:', { isAuthenticated, user });
  }, [isAuthenticated, user]);

  return (
    <div className="page-container">
      {/* 标题区域 */}
      <div className="text-center py-10 px-4">
        <Title level={1}>魔镜Mirror颜值PK平台</Title>
        <Paragraph className="text-lg mb-8">
          基于AI技术的颜值评分与PK对战平台，一起来挑战吧！
        </Paragraph>
        
        {isAuthenticated ? (
          <div className="space-x-4">
            <Link to="/scoring">
              <Button type="primary" size="large" icon={<CameraOutlined />}>
                开始评分
              </Button>
            </Link>
            <Link to="/battle">
              <Button size="large" icon={<ThunderboltOutlined />}>
                PK对战
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-x-4">
            <Link to="/login">
              <Button type="primary" size="large" icon={<UserOutlined />}>
                登录体验
              </Button>
            </Link>
            <Link to="/register">
              <Button size="large">
                立即注册
              </Button>
            </Link>
          </div>
        )}
      </div>

      {/* 功能介绍 */}
      <Row gutter={[24, 24]} className="mb-12">
        <Col xs={24} sm={12} lg={8}>
          <Card className="card-shadow h-full text-center">
            <CameraOutlined className="text-4xl text-primary mb-4" />
            <Title level={4}>颜值打分</Title>
            <Paragraph>
              使用先进的AI算法，精准评估您的颜值分数，发现自己的美丽指数
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="card-shadow h-full text-center">
            <ThunderboltOutlined className="text-4xl text-primary mb-4" />
            <Title level={4}>PK对战</Title>
            <Paragraph>
              与好友或陌生人进行颜值PK，赢取积分提升排名，展示个人魅力
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card className="card-shadow h-full text-center">
            <TrophyOutlined className="text-4xl text-primary mb-4" />
            <Title level={4}>排行榜</Title>
            <Paragraph>
              实时更新的全球/好友排行榜，看看谁是颜值巅峰，争夺榜首位置
            </Paragraph>
          </Card>
        </Col>
      </Row>

      {/* 使用说明 */}
      <Title level={2} className="text-center mb-8">如何使用</Title>
      <Row gutter={[24, 24]} className="mb-12">
        <Col xs={24} md={8}>
          <Card className="card-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mr-4">1</div>
              <Title level={4} className="m-0">上传照片</Title>
            </div>
            <Paragraph>
              上传您的清晰面部照片，要求光线充足，正面无遮挡，系统将自动检测并分析
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="card-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mr-4">2</div>
              <Title level={4} className="m-0">获取评分</Title>
            </div>
            <Paragraph>
              AI算法会综合分析您的面部特征，给出0-100分的客观评分，并提供详细分析
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="card-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-primary text-white rounded-full w-8 h-8 flex items-center justify-center mr-4">3</div>
              <Title level={4} className="m-0">参与PK</Title>
            </div>
            <Paragraph>
              选择好友或随机对手发起PK挑战，赢取积分提升排名，争夺颜值巅峰
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home; 