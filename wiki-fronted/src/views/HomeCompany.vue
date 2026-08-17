<template>
  <div class="home-page">
    <!-- 站点展示：品牌与核心能力（独立宣传页见路由 /welcome） -->
    <!-- <SiteShowcase /> -->
    <!-- 第一部分：Banner 轮播图 -->
    <section class="banner-section">
      <tiny-carousel
        :height="bannerHeight"
        :arrow="'hover'"
        :indicator-position="'outside'"
        :autoplay="true"
        :interval="5000"
        :loop="true"
      >
        <tiny-carousel-item
          v-for="(banner, index) in banners"
          :key="index"
          class="banner-item"
        >
          <div
            class="banner-content"
            :style="{ backgroundImage: `url(${banner.image})` }"
            @click="handleBannerClick(banner)"
          >
            <div class="banner-overlay">
              <div class="banner-text">
                <h2 class="banner-title">{{ banner.title }}</h2>
                <p class="banner-desc">{{ banner.description }}</p>
              </div>
            </div>
          </div>
        </tiny-carousel-item>
      </tiny-carousel>
    </section>
    <!-- 第二部分：最新文章 -->
    <section class="articles-section">
      <div class="articles-container">
        <div class="articles-layout">
          <!-- 最新发布 -->
          <div class="article-column">
            <div class="column-header">
              <h3 class="column-title">
                <svg class="title-icon" viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                  <path d="M832 512a32 32 0 1 1 64 0v352a32 32 0 0 1-32 32H160a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h352a32 32 0 0 1 0 64H192v640h640V512z"/>
                  <path d="M469.952 554.24l45.248-45.248 141.888 141.888-45.248 45.248zM832 128a32 32 0 0 1 9.408 62.592l-9.408 1.408-192 192a32 32 0 0 1-45.248-45.248L786.752 128H832z"/>
                </svg>
                {{ translate('home.latestPublished') }}
              </h3>
            </div>
            <div class="article-list">
              <div
                v-for="article in latestPublished"
                :key="article.id"
                class="article-item"
                @click="goToArticle(article.id, article.knowledgeBaseId)"
              >
                <div class="article-content">
                  <h4 class="article-title">{{ article.title }}</h4>
                  <p class="article-meta">
                    <span class="article-author">{{ article.author }}</span>
                    <span class="article-date">{{ formatDate(article.createdAt) }}</span>
                  </p>
                  <p class="article-excerpt">{{ article.excerpt }}</p>
                </div>
              </div>
              <div v-if="latestPublished.length === 0" class="empty-state">
                {{ translate('home.noArticles') }}
              </div>
            </div>
          </div>

          <!-- 最近更新 -->
          <div class="article-column">
            <div class="column-header">
              <h3 class="column-title">
                <svg class="title-icon" viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
                  <path d="M686.7 638.6L512 516.7V256c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v275.4l198.6 134.1c1.8 1.2 4 1.8 6.2 1.8 2.6 0 5.2-1 7.2-2.8 3.4-2.8 4.4-7.8 2.2-11.8l-48.7-84.1z"/>
                </svg>
                {{ translate('home.recentlyUpdated') }}
              </h3>
            </div>
            <div class="article-list">
              <div
                v-for="article in recentlyUpdated"
                :key="article.id"
                class="article-item"
                @click="goToArticle(article.id, article.knowledgeBaseId)"
              >
                <div class="article-content">
                  <h4 class="article-title">{{ article.title }}</h4>
                  <p class="article-meta">
                    <span class="article-author">{{ article.author }}</span>
                    <span class="article-date">{{ formatDate(article.updatedAt) }}</span>
                  </p>
                  <p class="article-excerpt">{{ article.excerpt }}</p>
                </div>
              </div>
              <div v-if="recentlyUpdated.length === 0" class="empty-state">
                {{ translate('home.noArticles') }}
              </div>
            </div>
          </div>

          <!-- 最近新增 -->
          <div class="article-column">
            <div class="column-header">
              <h3 class="column-title">
                <svg class="title-icon" viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
                  <path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z"/>
                </svg>
                {{ translate('home.recentlyAdded') }}
              </h3>
            </div>
            <div class="article-list">
              <div
                v-for="article in recentlyAdded"
                :key="article.id"
                class="article-item"
                @click="goToArticle(article.id, article.knowledgeBaseId)"
              >
                <div class="article-content">
                  <h4 class="article-title">{{ article.title }}</h4>
                  <p class="article-meta">
                    <span class="article-author">{{ article.author }}</span>
                    <span class="article-date">{{ formatDate(article.createdAt) }}</span>
                  </p>
                  <p class="article-excerpt">{{ article.excerpt }}</p>
                </div>
              </div>
              <div v-if="recentlyAdded.length === 0" class="empty-state">
                {{ translate('home.noArticles') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-bottom">
        <p>技术支持团队</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button as TinyButton, Carousel as TinyCarousel, CarouselItem as TinyCarouselItem, 
  Card as TinyCard} from '@opentiny/vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import defaultAvatar from '../assets/default-avatar.svg'
import { bannerApi, type Banner } from '../api/banner'
import { type ArticleSearchItem } from '../api/article'
import { useRecentArticlesStore } from '../stores/recentArticles'
import SiteShowcase from './SiteShowcase.vue'

const router = useRouter()
const localeStore = useLocaleStore()

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// Banner 数据（从后端接口获取）
const banners = ref<
  {
    title: string
    description: string
    image: string
    buttonText: string
    link: string
  }[]
>([])

// 文章数据（从接口获取，复用 recentArticlesStore，避免重复请求）
const recentArticlesStore = useRecentArticlesStore()

const latestPublished = computed<
  {
    id: number
    title: string
    author: string
    createdAt: Date
    excerpt: string
    knowledgeBaseId: number
  }[]
>(() =>
  (recentArticlesStore.recentCreated || []).map((item: ArticleSearchItem) => ({
    id: item.id,
    title: item.title,
    author: typeof item.author === 'string' ? item.author : String((item.author as any)?.name ?? item.author ?? ''),
    createdAt: item.created_at ? new Date(item.created_at) : new Date(),
    excerpt: (item.summary || '').slice(0, 80),
    knowledgeBaseId: item.knowledge_base_id
  }))
)

const recentlyUpdated = computed<
  {
    id: number
    title: string
    author: string
    updatedAt: Date
    excerpt: string
    knowledgeBaseId: number
  }[]
>(() =>
  (recentArticlesStore.recentUpdated || []).map((item: ArticleSearchItem) => ({
    id: item.id,
    title: item.title,
    author: typeof item.author === 'string' ? item.author : typeof item.updated_by_name === 'string' ? item.updated_by_name : String((item.author as any)?.name ?? item.author ?? ''),
    updatedAt: item.updated_at ? new Date(item.updated_at) : new Date(),
    excerpt: (item.summary || '').slice(0, 80),
    knowledgeBaseId: item.knowledge_base_id
  }))
)

// “最近新增” 暂时与 “最新发布” 使用相同数据
const recentlyAdded = computed(() => latestPublished.value)

// Banner 高度
const bannerHeight = computed(() => {
  return '300px'
})

// 格式化日期
const formatDate = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))

  if (days > 0) {
    return `${days}${translate('home.daysAgo')}`
  } else if (hours > 0) {
    return `${hours}${translate('home.hoursAgo')}`
  } else if (minutes > 0) {
    return `${minutes}${translate('home.minutesAgo')}`
  } else {
    return translate('home.justNow')
  }
}

// 头像加载错误处理
const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src = defaultAvatar
}

// 导航函数
const handleBannerClick = (banner: { link: string }) => {
  if (banner.link) {
    window.open(banner.link, '_blank')
  }
}

const goToUserProfile = (userId: number) => {
  router.push(`/user/${userId}`)
}

const goToArticle = (articleId: number, knowledgeBaseId: number) => {
  window.open(`/articles/${knowledgeBaseId}?articleId=${articleId}`, '_blank')
}

// 组件挂载时从接口获取 Banner 和首页文章数据
onMounted(async () => {
  try {
    const res = await bannerApi.getBanners({
      page: 1,
      page_size: 10,
      status: 1
    })
    // 将后端 Banner 数据映射到首页展示结构
    banners.value = (res.items || [])
      .sort((a: Banner, b: Banner) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
      .map((item: Banner) => ({
        // 支持使用 `标题|描述` 的形式配置文案
        title: (item.title || '').split('|')[0]?.trim() || item.title,
        description: (item.title || '').includes('|')
          ? (item.title || '').split('|')[1]?.trim() || ''
          : item.description || '',
        image: item.image_url,
        buttonText: translate('home.banner.button'),
        link: item.link_url || ''
      }))
  } catch (e) {
    // 如果接口失败，可以考虑保持空数组或后续扩展为降级展示默认 Banner
    banners.value = []
  }

  // 加载最新发布 / 最近更新文章（store 内部会做去重）
  await recentArticlesStore.fetchRecentArticles()
})
</script>

<style scoped lang="less">
.home-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  overflow-x: hidden;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

// 第一部分：Banner 轮播图
.banner-section {
  width: 100%;

  :deep(.tiny-carousel) {
    .tiny-carousel__indicators {
      bottom: 20px;
    }

    .tiny-carousel__indicator {
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      margin: 0 5px;

      &.is-active {
        background: var(--primary-color, #8b5cf6);
      }
    }

    .tiny-carousel__arrow {
      background: rgba(255, 255, 255, 0.8);
      color: var(--primary-color, #8b5cf6);
      border-radius: 50%;
      width: 40px;
      height: 40px;

      &:hover {
        background: var(--primary-color, #8b5cf6);
        color: #fff;
      }
    }
  }

  .banner-item {
    .banner-content {
      width: 100%;
      height: 300px;
      margin: 0 auto;
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      position: relative;
    }

    .banner-overlay {

      display: flex;
      align-items: flex-end;
      justify-content: flex-start;
      padding: 40px 60px;
    }

    .banner-text {
      text-align: left;
      color: #fff;
      max-width: 600px;

      .banner-title {
        font-size: 40px;
        font-weight: 700;
        margin: 0 0 12px 0;
        line-height: 1.2;
      }

      .banner-desc {
        font-size: 20px;
        margin: 0;
        line-height: 1.6;
        opacity: 0.95;
      }
    }
  }
}


// 第二部分：最新文章（全宽三列均分）
.articles-section {
  padding: 60px 0;
  background: #f5f7fa;
  width: 100%;
  box-sizing: border-box;

  .articles-container {
    width: 100%;
    max-width: none;
    margin: 0 auto;
    padding: 0 clamp(16px, 3vw, 48px);
    box-sizing: border-box;
  }

  .articles-layout {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(16px, 2vw, 32px);
    width: 100%;
  }

  .article-column {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s;
    display: flex;
    flex-direction: column;
    min-width: 0;
    height: 420px;

    &:hover {
      box-shadow: 0 4px 16px rgba(139, 92, 246, 0.1);
    }

    .column-header {
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 2px solid var(--primary-color, #8b5cf6);

      .column-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 20px;
        font-weight: 600;
        color: #333;
        margin: 0;

        .title-icon {
          color: var(--primary-color, #8b5cf6);
        }
      }
    }

    .article-list {
      flex: 1;
      overflow-y: auto;

      .article-item {
        padding: 10px 0;
        border-bottom: 1px solid #e4e7ed;
        cursor: pointer;
        transition: all 0.3s;

        &:last-child {
          border-bottom: none;
        }

        &:hover {
          padding-left: 8px;
          border-left: 3px solid var(--primary-color, #8b5cf6);

          .article-title {
            color: var(--primary-color, #8b5cf6);
          }
        }

        .article-content {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 10px 12px;
          flex-wrap: nowrap;
          min-width: 0;

          .article-title {
            flex: 1 1 0;
            min-width: 0;
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin: 0;
            line-height: 1.35;
            transition: color 0.3s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .article-meta {
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
            font-size: 11px;
            color: #999;
            white-space: nowrap;

            .article-author {
              color: var(--primary-color, #8b5cf6);
              font-weight: 500;
            }

            .article-date {
              &::before {
                content: '•';
                margin-right: 8px;
              }
            }
          }

          .article-excerpt {
            flex: 1.1 1 0;
            min-width: 0;
            font-size: 12px;
            color: #666;
            line-height: 1.35;
            margin: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
      }

      .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #999;
        font-size: 14px;
      }
    }
  }
}

// 底部
.footer {
  background: #1a1a1a;
  color: #fff;
  margin-top: auto;
}

.footer-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 40px 40px;
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 60px;
}

.footer-section {
  .footer-title {
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 15px 0;
    color: var(--primary-color, #8b5cf6);
  }

  .footer-desc {
    font-size: 14px;
    color: #999;
    margin: 0;
    line-height: 1.6;
  }
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.link-group {
  .link-title {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 20px 0;
    color: #fff;
  }

  .link-item {
    display: block;
    color: #999;
    text-decoration: none;
    font-size: 14px;
    margin-bottom: 12px;
    transition: color 0.3s;

    &:hover {
      color: var(--primary-color, #8b5cf6);
    }
  }

  .contact-item {
    color: #999;
    font-size: 14px;
    margin-bottom: 12px;
  }
}

.footer-bottom {
  border-top: 1px solid #333;
  padding: 20px;
  text-align: center;

  p {
    margin: 0;
    font-size: 12px;
    color: #999;

    a {
      color: #999;
      text-decoration: none;

      &:hover {
        color: var(--primary-color, #8b5cf6);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .articles-section .articles-layout {
    grid-template-columns: 1fr;
  }

  .contributors-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 20px;
  }

  .banner-section {
    .banner-item {
      .banner-overlay {
        padding: 40px 20px;
      }

      .banner-text {
        .banner-title {
          font-size: 32px;
        }

        .banner-desc {
          font-size: 16px;
        }
      }
    }
  }

  .ranking-section {
    padding: 40px 0;

    .section-title {
      font-size: 24px;
      margin-bottom: 30px;
    }

    .contributors-grid {
      grid-template-columns: 1fr !important;
      gap: 20px;
    }
  }

  .articles-section {
    padding: 40px 0;

    .articles-container {
      padding: 0 16px;
    }

    .articles-layout {
      gap: 20px;
    }

    .article-column {
      padding: 20px;
    }
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 40px;
    padding: 40px 20px 30px;
  }

  .footer-links {
    grid-template-columns: 1fr;
    gap: 30px;
  }
}
</style>
