import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Avatar, Image, Spin, message } from 'antd';
import { UserOutlined, CrownOutlined, ReloadOutlined } from '@ant-design/icons';
import { getGlobalRankings } from '../services/api';
import { useNavigate } from 'react-router-dom';

// 排行榜用户数据接口
interface RankingUser {
  rank: number;
  user_id: number;
  score_id: number;
  username: string;
  nickname: string;
  avatar: string;
  highest_score: number;
  image_url: string;
  scored_at: string;
}

// 简单的占位图片URL，替代长base64字符串
const PLACEHOLDER_IMAGE = 'https://gw.alipayobjects.com/zos/antfincdn/aPkFc8Sj7n/method-draw-image.svg';

const Rankings: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [rankings, setRankings] = useState<RankingUser[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  // 用于存储已加载的图片缓存键
  const [loadedImageKeys, setLoadedImageKeys] = useState<Set<string>>(new Set());

  // 清除图片缓存的函数
  const clearImageCache = useCallback(() => {
    setLoadedImageKeys(new Set());
  }, []);

  const fetchRankings = async (page = 1, limit = 10) => {
    setLoading(true);
    try {
      // 在获取新数据前清除图片缓存
      clearImageCache();
      
      const response = await getGlobalRankings(page, limit);
      console.log('排行榜响应:', response); // 添加调试日志
      
      // 修改为正确获取response.data内容
      if (response && response.data) {
        setRankings(response.data.data);
        setTotal(response.data.total || 0);
        setCurrentPage(response.data.page || 1);
        setPageSize(response.data.limit || 10);
      }
    } catch (error) {
      console.error('获取排行榜失败', error);
      message.error('获取排行榜数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 检查是否需要强制刷新排行榜
    const shouldRefresh = sessionStorage.getItem('refreshRankings');
    if (shouldRefresh === 'true') {
      // 清除标志
      sessionStorage.removeItem('refreshRankings');
      // 强制刷新排行榜
      fetchRankings();
      message.info('排行榜已更新');
    } else {
      // 正常加载
      fetchRankings();
    }
  }, []);

  const handleRefresh = () => {
    fetchRankings(currentPage, pageSize);
    message.success('数据已刷新');
  };

  // 处理分页变化
  const handlePageChange = (page: number, pageSize?: number) => {
    // 在页面切换时清除图片缓存
    clearImageCache();
    fetchRankings(page, pageSize || 10);
  };

  // 生成唯一的图片键，用于缓存控制
  const getImageKey = (imageUrl: string, rank: number) => {
    return `${imageUrl}_${rank}_${currentPage}`;
  };

  const columns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (rank: number) => {
        // 只有全局排名第一的用户显示皇冠图标，而不是每页的第一个
        if (rank === 1) {
          return (
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-500 text-white mx-auto">
              <CrownOutlined />
            </div>
          );
        }
        return <div className="text-center font-medium">{rank}</div>;
      }
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (text: string, record: RankingUser) => (
        <div className="flex items-center">
          <Avatar 
            icon={<UserOutlined />} 
            src={record.avatar} 
          />
          <span className="ml-2">
            {record.nickname || text}
          </span>
        </div>
      )
    },
    {
      title: '照片',
      dataIndex: 'image_url',
      key: 'image',
      render: (imageUrl: string, record: RankingUser) => {
        // 为每个图片生成唯一的键
        const imageKey = getImageKey(imageUrl, record.rank);
        
        return (
          <div className="flex flex-col items-center">
            {imageUrl ? (
              <Image 
                src={imageUrl.startsWith('http') ? imageUrl : `http://localhost:8000${imageUrl}?t=${Date.now()}`} 
                width={80} 
                height={80} 
                className="object-cover rounded-lg border border-gray-200"
                fallback={PLACEHOLDER_IMAGE}
                key={imageKey} // 添加唯一键，确保页面切换时重新加载图片
              />
            ) : (
              <div className="w-20 h-20 bg-gray-100 flex items-center justify-center rounded-lg border border-gray-200">
                <span className="text-gray-500 text-xs">无图片</span>
              </div>
            )}
          </div>
        );
      }
    },
    {
      title: '分数',
      dataIndex: 'highest_score',
      key: 'highest_score',
      render: (score: number) => (
        <div className="text-lg font-bold">
          {score ? score.toFixed(1) : "0.0"}
        </div>
      )
    },
    {
      title: '评分时间',
      dataIndex: 'scored_at',
      key: 'scored_at',
      render: (scored_at: string) => {
        if (!scored_at) return <span>-</span>;
        const date = new Date(scored_at);
        return <span>{date.toLocaleDateString()}</span>;
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: RankingUser) => (
        <Button 
          type="primary"
          size="small"
          onClick={() => {
            navigate('/battle', { 
              state: { 
                opponent: {
                  id: record.user_id,
                  username: record.nickname || record.username,
                  avatar: record.avatar,
                  score: record.highest_score,
                  image_url: record.image_url,
                  rank: record.rank,
                  score_id: record.score_id
                }
              } 
            });
          }}
        >
          PK
        </Button>
      )
    }
  ];

  return (
    <div className="page-container">
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-bold mb-0">颜值排行榜</h2>
        </div>
        <div className="p-4">
          <div className="flex justify-end mb-4">
            <Button 
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={loading}
            >
              刷新
            </Button>
          </div>
          
          <Spin spinning={loading} tip="加载中...">
            <Table 
              columns={columns} 
              dataSource={rankings} 
              rowKey={(record) => `${record.user_id}_${record.rank}_${currentPage}`} 
              pagination={{
                total: total,
                current: currentPage,
                pageSize: pageSize,
                onChange: handlePageChange,
                showSizeChanger: true
              }}
              locale={{
                emptyText: '暂无数据'
              }}
              className="rankings-table"
              rowClassName={(record) => record.rank <= 3 ? `rank-${record.rank}` : ''}
            />
          </Spin>
        </div>
      </div>
    </div>
  );
};

export default Rankings;