<template>
  <section class="site-showcase" aria-labelledby="site-showcase-headline" id="site-showcase-top">
    <!-- 语雀式：上区双栏（左文案 + 右产品示意），浅色大留白 -->
    <div class="site-showcase__hero-slab">
      <div class="site-showcase__inner site-showcase__hero-grid">
        <div class="site-showcase__copy">
          <p class="site-showcase__badge">{{ translate('siteShowcase.badge') }}</p>
          <h1 id="site-showcase-headline" class="site-showcase__headline">
            {{ translate('siteShowcase.headline') }}
          </h1>
          <p class="site-showcase__subline">{{ translate('siteShowcase.subline') }}</p>
          <p class="site-showcase__lead">{{ translate('siteShowcase.lead') }}</p>
          <div class="site-showcase__actions">
            <tiny-button type="primary" size="medium" @click="goKnowledgeSpace">
              {{ translate('siteShowcase.enterKnowledge') }}
            </tiny-button>
            <tiny-button size="medium" @click="goPersonalCenter">
              {{ translate('siteShowcase.enterPersonal') }}
            </tiny-button>
          </div>
        </div>

        <div
          class="site-showcase__visual"
          role="img"
          :aria-label="translate('siteShowcase.heroPreviewLabel')"
        >
          <div class="site-showcase__mock">
            <div class="site-showcase__mock-chrome">
              <span class="site-showcase__mock-dot" />
              <span class="site-showcase__mock-dot" />
              <span class="site-showcase__mock-dot" />
              <div class="site-showcase__mock-url" aria-hidden="true" />
            </div>
            <div class="site-showcase__mock-body">
              <aside class="site-showcase__mock-sidebar" aria-hidden="true">
                <span class="site-showcase__mock-nav site-showcase__mock-nav--active" />
                <span class="site-showcase__mock-nav" />
                <span class="site-showcase__mock-nav" />
                <span class="site-showcase__mock-nav" />
              </aside>
              <div class="site-showcase__mock-editor" aria-hidden="true">
                <div class="site-showcase__mock-toolbar">
                  <span /><span /><span />
                </div>
                <div class="site-showcase__mock-title-line" />
                <div class="site-showcase__mock-line site-showcase__mock-line--long" />
                <div class="site-showcase__mock-line site-showcase__mock-line--med" />
                <div class="site-showcase__mock-line site-showcase__mock-line--long" />
                <div class="site-showcase__mock-line site-showcase__mock-line--short" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="site-showcase-features" class="site-showcase__features-slab">
      <div class="site-showcase__inner">
        <header class="site-showcase__section-head">
          <h2 class="site-showcase__features-title">{{ translate('siteShowcase.featuresTitle') }}</h2>
          <p class="site-showcase__features-sub">{{ translate('siteShowcase.featuresSubtitle') }}</p>
        </header>
        <div class="site-showcase__features">
          <article v-for="(f, i) in featureItems" :key="i" class="site-showcase__card">
            <div class="site-showcase__card-icon" aria-hidden="true">
              <component :is="f.icon" />
            </div>
            <h3 class="site-showcase__card-title">{{ translate(f.titleKey) }}</h3>
            <p class="site-showcase__card-desc">{{ translate(f.descKey) }}</p>
          </article>
        </div>
      </div>
    </div>

    <div class="site-showcase__cta-band">
      <div class="site-showcase__inner site-showcase__cta-inner">
        <div class="site-showcase__cta-copy">
          <h2 class="site-showcase__cta-title">{{ translate('siteShowcase.bottomCtaTitle') }}</h2>
          <p class="site-showcase__cta-desc">{{ translate('siteShowcase.bottomCtaDesc') }}</p>
        </div>
        <tiny-button type="primary" size="medium" class="site-showcase__cta-btn" @click="goKnowledgeSpace">
          {{ translate('siteShowcase.enterKnowledge') }}
        </tiny-button>
      </div>
    </div>

    <!-- 语雀式页脚：左品牌/社群 + 右三列导航 + 底栏备案说明 -->
    <footer class="site-showcase__footer" aria-labelledby="site-showcase-footer-heading">
      <div class="site-showcase__inner">
        <div class="site-showcase__footer-main">
          <div class="site-showcase__footer-brand">
            <h2 id="site-showcase-footer-heading" class="site-showcase__footer-logo">
              {{ translate('siteShowcase.footer.brandName') }}
            </h2>
            <p class="site-showcase__footer-slogan">{{ translate('siteShowcase.footer.slogan') }}</p>
            <div class="site-showcase__footer-social" aria-label="social">
              <a
                v-for="s in socialLinks"
                :key="s.name"
                class="site-showcase__footer-social-link"
                :href="s.href"
                target="_blank"
                rel="noopener noreferrer"
                :aria-label="translate(s.labelKey)"
              >
                <component :is="s.icon" />
              </a>
            </div>
            <div class="site-showcase__footer-qr-row">
              <div class="site-showcase__footer-qr-wrap">
                <img
                  class="site-showcase__footer-qr-img"
                  src="https://zs-wiki.obs.cn-south-1.myhuaweicloud.com/wiki/2026-04-04/98f4cd45f488e0614e5767ad870530f0_0fedc4b2.png"
                  width="88"
                  height="88"
                  :alt="translate('siteShowcase.footer.qrTitle')"
                  loading="lazy"
                  decoding="async"
                />
              </div>
              <div class="site-showcase__footer-qr-text">
                <p class="site-showcase__footer-qr-title">{{ translate('siteShowcase.footer.qrTitle') }}</p>
                <p class="site-showcase__footer-qr-sub">{{ translate('siteShowcase.footer.qrSub') }}</p>
              </div>
            </div>
          </div>

          <nav class="site-showcase__footer-nav" aria-label="footer">
            <div class="site-showcase__footer-col">
              <h3 class="site-showcase__footer-col-title">{{ translate('siteShowcase.footer.colProduct') }}</h3>
              <ul class="site-showcase__footer-links">
                <li v-for="item in footerProductLinks" :key="item.key">
                  <a :href="item.href" class="site-showcase__footer-link" @click="onFooterLink($event, item)">
                    {{ translate(item.labelKey) }}
                  </a>
                </li>
              </ul>
            </div>
            <div class="site-showcase__footer-col">
              <h3 class="site-showcase__footer-col-title">{{ translate('siteShowcase.footer.colService') }}</h3>
              <ul class="site-showcase__footer-links">
                <li v-for="item in footerServiceLinks" :key="item.key">
                  <a :href="item.href" class="site-showcase__footer-link" @click="onFooterLink($event, item)">
                    {{ translate(item.labelKey) }}
                  </a>
                </li>
              </ul>
            </div>
            <div class="site-showcase__footer-col">
              <h3 class="site-showcase__footer-col-title">{{ translate('siteShowcase.footer.colAbout') }}</h3>
              <ul class="site-showcase__footer-links">
                <li v-for="item in footerAboutLinks" :key="item.key">
                  <a :href="item.href" class="site-showcase__footer-link" @click="onFooterLink($event, item)">
                    {{ translate(item.labelKey) }}
                  </a>
                </li>
              </ul>
            </div>
          </nav>
        </div>

        <div class="site-showcase__footer-contact-bar">
          <h3 class="site-showcase__footer-contact-title">
            {{ translate('siteShowcase.footer.contactTitle') }}
          </h3>
          <ul class="site-showcase__footer-contact-list">
            <li class="site-showcase__footer-contact-item">
              <span class="site-showcase__footer-contact-label">{{
                translate('siteShowcase.footer.contact.email')
              }}</span>
              <a class="site-showcase__footer-contact-value" :href="`mailto:${footerContact.email}`">{{
                footerContact.email
              }}</a>
            </li>
            <li class="site-showcase__footer-contact-item">
              <span class="site-showcase__footer-contact-label">{{
                translate('siteShowcase.footer.contact.phone')
              }}</span>
              <a class="site-showcase__footer-contact-value" :href="`tel:${footerContact.phoneTel}`">{{
                footerContact.phoneDisplay
              }}</a>
            </li>
            <li class="site-showcase__footer-contact-item">
              <span class="site-showcase__footer-contact-label">{{
                translate('siteShowcase.footer.contact.wechat')
              }}</span>
              <span class="site-showcase__footer-contact-value site-showcase__footer-contact-value--plain">{{
                footerContact.wechatId
              }}</span>
            </li>
          </ul>
        </div>

        <div class="site-showcase__footer-legal" role="contentinfo">
          <p class="site-showcase__footer-legal-text">
            {{ translate('siteShowcase.footer.legalLine', { year: String(currentYear) }) }}
          </p>
        </div>
      </div>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { Button as TinyButton } from '@opentiny/vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const router = useRouter()
const localeStore = useLocaleStore()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const currentYear = new Date().getFullYear()

/** 页脚展示用联系方式（可按需修改） */
const footerContact = {
  email: '1710695204@qq.com',
  phoneDisplay: '15913848494',
  phoneTel: '15913848494',
  wechatId: 'zs1710695204',
}

type FooterLinkItem = {
  key: string
  labelKey: string
  href: string
  /** 站内路由，优先于 href */
  route?: string
}

const footerProductLinks: FooterLinkItem[] = [
  { key: 'core', labelKey: 'siteShowcase.footer.link.core', href: '#site-showcase-features' },
  { key: 'news', labelKey: 'siteShowcase.footer.link.news', href: '/', route: '/' },
  { key: 'team', labelKey: 'siteShowcase.footer.link.team', href: '/knowledge/team-spaces', route: '/knowledge/team-spaces' },
  { key: 'cases', labelKey: 'siteShowcase.footer.link.cases', href: '#site-showcase-top' },
  { key: 'pricing', labelKey: 'siteShowcase.footer.link.pricing', href: '#site-showcase-features' },
]

const footerServiceLinks: FooterLinkItem[] = [
  { key: 'help', labelKey: 'siteShowcase.footer.link.help', href: '#site-showcase-features' },
  { key: 'security', labelKey: 'siteShowcase.footer.link.security', href: '#site-showcase-features' },
  { key: 'terms', labelKey: 'siteShowcase.footer.link.terms', href: '#site-showcase-top' },
  { key: 'dev', labelKey: 'siteShowcase.footer.link.dev', href: '#site-showcase-top' },
  { key: 'feedback', labelKey: 'siteShowcase.footer.link.feedback', href: '/knowledge/my-feedbacks', route: '/knowledge/my-feedbacks' },
]

const footerAboutLinks: FooterLinkItem[] = [
  { key: 'about', labelKey: 'siteShowcase.footer.link.aboutSite', href: '#site-showcase-top' },
  { key: 'blog', labelKey: 'siteShowcase.footer.link.column', href: '#site-showcase-features' },
  { key: 'media', labelKey: 'siteShowcase.footer.link.media', href: '#site-showcase-top' },
  { key: 'contact', labelKey: 'siteShowcase.footer.link.contact', href: '#site-showcase-top' },
  { key: 'join', labelKey: 'siteShowcase.footer.link.join', href: '#site-showcase-top' },
]

function onFooterLink(e: MouseEvent, item: FooterLinkItem) {
  if (item.route) {
    e.preventDefault()
    router.push(item.route).catch(() => {})
    return
  }
  if (item.href.startsWith('#')) {
    e.preventDefault()
    const id = item.href.slice(1)
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const IconWechat = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', 'aria-hidden': 'true' }, [
    h('path', {
      d: 'M8.5 9.5a1.2 1.2 0 1 1 0-2.4 1.2 1.2 0 0 1 0 2.4zm7 0a1.2 1.2 0 1 1 0-2.4 1.2 1.2 0 0 1 0 2.4zM5.8 14.8c.5 1.1 1.6 2 3 2.5l-.6 1.8 2-1c.8.2 1.6.3 2.4.3 4.2 0 7.6-2.6 7.6-5.8 0-1.6-.8-3.1-2.2-4.2.3-.7.5-1.5.5-2.3C18.5 4.7 15 2 10.7 2S3 4.7 3 8c0 1.9.9 3.6 2.4 4.8-.2.7-.4 1.4-.4 2.2 0 .3 0 .6.1.8z',
    }),
  ])

const IconWeibo = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', 'aria-hidden': 'true' }, [
    h('path', {
      d: 'M10.1 19.8c-4.1 0-7.4-2.2-7.4-5 0-1.6 1-3 2.7-4-.3-1-.1-2.1.6-3 .7-.9 1.8-1.4 3-1.4.4 0 .8 0 1.2.1 1.3-1.2 3.2-2 5.3-2 4 0 7.3 2.4 7.3 5.4 0 .6-.1 1.2-.3 1.8 1.3 1 2.1 2.3 2.1 3.7 0 3.2-4.5 5.8-10 5.8z',
    }),
  ])

const IconZhihu = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', 'aria-hidden': 'true' }, [
    h('path', {
      d: 'M6 4h7l1.8 5.4h.1L16.5 4H20v16h-3V8.9h-.1L14.5 20h-3L9.1 9.2H9V20H6V4z',
    }),
  ])

const IconMail = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'aria-hidden': 'true' }, [
    h('rect', { x: '2', y: '4', width: '20', height: '16', rx: '2' }),
    h('path', { d: 'm22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7' }),
  ])

const socialLinks = [
  // { name: 'wechat', href: '#site-showcase-footer-heading', labelKey: 'siteShowcase.footer.social.wechat', icon: IconWechat },
  // { name: 'weibo', href: 'https://weibo.com', labelKey: 'siteShowcase.footer.social.weibo', icon: IconWeibo },
  { name: 'zhihu', href: 'https://www.zhihu.com', labelKey: 'siteShowcase.footer.social.zhihu', icon: IconZhihu },
  { name: 'mail', href: 'mailto:', labelKey: 'siteShowcase.footer.social.mail', icon: IconMail },
]

/** 简洁 SVG 图标（内联，不依赖额外资源） */
const IconDoc = () =>
  h(
    'svg',
    { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' },
    [
      h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
      h('polyline', { points: '14 2 14 8 20 8' }),
      h('line', { x1: '16', y1: '13', x2: '8', y2: '13' }),
      h('line', { x1: '16', y1: '17', x2: '8', y2: '17' }),
    ]
  )

const IconShield = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }),
  ])

const IconDevices = () =>
  h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('rect', { x: '2', y: '3', width: '20', height: '14', rx: '2', ry: '2' }),
    h('line', { x1: '8', y1: '21', x2: '16', y2: '21' }),
    h('line', { x1: '12', y1: '17', x2: '12', y2: '21' }),
  ])

const featureItems = computed(() => [
  { titleKey: 'feature.wysiwyg.title', descKey: 'feature.wysiwyg.desc', icon: IconDoc },
  { titleKey: 'feature.security.title', descKey: 'feature.security.desc', icon: IconShield },
  { titleKey: 'feature.responsive.title', descKey: 'feature.responsive.desc', icon: IconDevices },
])

function goKnowledgeSpace() {
  router.push({ path: '/knowledge/knowledge-spaces' })
}

function goPersonalCenter() {
  router.push({ path: '/knowledge/personal-center' })
}
</script>

<style scoped lang="less">
.site-showcase {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.site-showcase__inner {
  max-width: 1120px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box;
}

/* —— Hero：左文右图 —— */
.site-showcase__hero-slab {
  padding: 48px 0 56px;
  background:
    radial-gradient(ellipse 90% 70% at 100% 0%, color-mix(in srgb, var(--primary-color, #8b5cf6) 12%, transparent), transparent 50%),
    radial-gradient(ellipse 70% 50% at 0% 100%, color-mix(in srgb, var(--primary-color, #8b5cf6) 8%, transparent), transparent 45%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-bottom: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 10%, #e2e8f0);
}

.site-showcase__hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
  gap: clamp(32px, 5vw, 64px);
  align-items: center;
}

.site-showcase__copy {
  text-align: left;
}

.site-showcase__badge {
  display: inline-block;
  margin: 0 0 14px;
  padding: 5px 14px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-color, #7c3aed);
  background: color-mix(in srgb, var(--primary-color, #8b5cf6) 12%, transparent);
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 22%, transparent);
}

.site-showcase__headline {
  margin: 0 0 14px;
  font-size: clamp(28px, 4.2vw, 42px);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: #0f172a;
}

.site-showcase__subline {
  margin: 0 0 10px;
  font-size: clamp(16px, 2vw, 19px);
  font-weight: 500;
  line-height: 1.45;
  color: #334155;
}

.site-showcase__lead {
  margin: 0 0 28px;
  max-width: 520px;
  font-size: 15px;
  line-height: 1.7;
  color: #64748b;
}

.site-showcase__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* 右侧产品示意（浏览器 + 侧栏 + 编辑区） */
.site-showcase__visual {
  perspective: 1200px;
}

.site-showcase__mock {
  border-radius: 14px;
  background: #fff;
  border: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 14%, #e2e8f0);
  box-shadow:
    0 24px 48px -12px color-mix(in srgb, var(--primary-color, #7c3aed) 18%, transparent),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
  overflow: hidden;
  transform: rotateY(-6deg) rotateX(4deg);
  transition:
    transform 0.45s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.45s ease;

  @media (prefers-reduced-motion: no-preference) {
    animation: site-showcase-mock-desk 7s ease-in-out infinite;
  }

  &:hover {
    transform: rotateY(-3deg) rotateX(2deg) translateY(-4px);
    box-shadow:
      0 32px 64px -16px color-mix(in srgb, var(--primary-color, #7c3aed) 22%, transparent),
      0 0 0 1px rgba(255, 255, 255, 0.9) inset;
  }
}

@keyframes site-showcase-mock-desk {
  0%,
  100% {
    transform: rotateY(-6deg) rotateX(4deg) translateY(0);
  }
  50% {
    transform: rotateY(-6deg) rotateX(4deg) translateY(-8px);
  }
}

.site-showcase__mock-chrome {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: linear-gradient(180deg, #f1f5f9 0%, #e8eef5 100%);
  border-bottom: 1px solid #e2e8f0;
}

.site-showcase__mock-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e1;

  &:nth-child(1) {
    background: #fca5a5;
  }
  &:nth-child(2) {
    background: #fcd34d;
  }
  &:nth-child(3) {
    background: #86efac;
  }
}

.site-showcase__mock-url {
  flex: 1;
  height: 28px;
  margin-left: 8px;
  border-radius: 6px;
  background: #fff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.site-showcase__mock-body {
  display: flex;
  min-height: 220px;
}

.site-showcase__mock-sidebar {
  width: 22%;
  min-width: 72px;
  padding: 14px 10px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.site-showcase__mock-nav {
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  opacity: 0.85;

  &--active {
    background: color-mix(in srgb, var(--primary-color, #8b5cf6) 35%, #e9d5ff);
    opacity: 1;
  }
}

.site-showcase__mock-editor {
  flex: 1;
  padding: 14px 16px 20px;
  background: #fff;
}

.site-showcase__mock-toolbar {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;

  span {
    width: 28px;
    height: 8px;
    border-radius: 4px;
    background: #e2e8f0;

    &:first-child {
      width: 36px;
      background: color-mix(in srgb, var(--primary-color, #8b5cf6) 25%, #e2e8f0);
    }
  }
}

.site-showcase__mock-title-line {
  height: 14px;
  width: 58%;
  border-radius: 4px;
  margin-bottom: 16px;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--primary-color, #8b5cf6) 45%, #c4b5fd) 0%,
    #e2e8f0 100%
  );
}

.site-showcase__mock-line {
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  margin-bottom: 10px;

  &--long {
    width: 100%;
  }
  &--med {
    width: 88%;
  }
  &--short {
    width: 42%;
    margin-bottom: 0;
  }
}

/* —— 能力区块：居中标题 + 三卡 —— */
.site-showcase__features-slab {
  padding: 56px 0 48px;
  background: #fff;
}

.site-showcase__section-head {
  text-align: center;
  max-width: 640px;
  margin: 0 auto 36px;
}

.site-showcase__features-title {
  margin: 0 0 12px;
  font-size: clamp(20px, 2.5vw, 26px);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.site-showcase__features-sub {
  margin: 0;
  font-size: 15px;
  line-height: 1.65;
  color: #64748b;
}

.site-showcase__features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.site-showcase__card {
  padding: 24px 20px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 12%, #e2e8f0);
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease,
    background 0.25s ease;

  &:hover {
    transform: translateY(-3px);
    background: #fff;
    box-shadow: 0 16px 40px -12px color-mix(in srgb, var(--primary-color, #7c3aed) 15%, transparent);
  }
}

.site-showcase__card-icon {
  width: 44px;
  height: 44px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: var(--primary-color, #7c3aed);
  background: color-mix(in srgb, var(--primary-color, #8b5cf6) 12%, transparent);

  :deep(svg) {
    width: 22px;
    height: 22px;
  }
}

.site-showcase__card-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.site-showcase__card-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #64748b;
}

/* —— 底部 CTA 带（语雀常见通栏引导） —— */
.site-showcase__cta-band {
  padding: 40px 20px 48px;
  background: var(--primary-gradient, linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%));
  color: #fff;
}

.site-showcase__cta-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.site-showcase__cta-title {
  margin: 0 0 8px;
  font-size: clamp(18px, 2.2vw, 22px);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.site-showcase__cta-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  opacity: 0.92;
  max-width: 520px;
}

.site-showcase__actions :deep(.tiny-button--primary),
.site-showcase__cta-btn :deep(.tiny-button--primary) {
  background: var(--primary-gradient, linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%));
  border-color: transparent;
  box-shadow: 0 4px 18px color-mix(in srgb, var(--primary-color, #6d28d9) 45%, transparent);
}

.site-showcase__cta-btn :deep(.tiny-button--primary) {
  background: #fff;
  color: var(--primary-color, #7c3aed);
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.12);
}

.site-showcase__actions :deep(.tiny-button:not(.tiny-button--primary)) {
  border-color: color-mix(in srgb, var(--primary-color, #8b5cf6) 28%, #cbd5e1);
  color: var(--primary-color, #5b21b6);
  background: rgba(255, 255, 255, 0.95);
}

@media (max-width: 960px) {
  .site-showcase__hero-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .site-showcase__copy {
    text-align: center;
  }

  .site-showcase__lead {
    margin-left: auto;
    margin-right: auto;
  }

  .site-showcase__actions {
    justify-content: center;
  }

  .site-showcase__visual {
    max-width: 420px;
    margin: 0 auto;
  }

  .site-showcase__mock {
    transform: none;

    @media (prefers-reduced-motion: no-preference) {
      animation-name: site-showcase-mock-mob;
    }

    &:hover {
      transform: translateY(-4px);
    }
  }
}

@keyframes site-showcase-mock-mob {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

@media (max-width: 900px) {
  .site-showcase__features {
    grid-template-columns: 1fr;
  }

  .site-showcase__cta-inner {
    flex-direction: column;
    text-align: center;
  }

  .site-showcase__cta-copy {
    text-align: center;
  }
}

/* —— 页脚（语雀式：浅底、左品牌 + 右三列 + 底栏） —— */
.site-showcase__footer {
  margin-top: 0;
  padding: 48px 0 0;
  background: #f4f5f7;
  border-top: 1px solid #e8eaed;
  color: #3c4043;
}

.site-showcase__footer-main {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 2fr);
  gap: clamp(32px, 5vw, 56px);
  padding-bottom: 40px;
}

.site-showcase__footer-logo {
  margin: 0 0 10px;
  font-size: clamp(22px, 2.5vw, 28px);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #202124;
}

.site-showcase__footer-slogan {
  margin: 0 0 20px;
  font-size: 14px;
  line-height: 1.55;
  color: #5f6368;
  max-width: 280px;
}

.site-showcase__footer-social {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.site-showcase__footer-social-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #5f6368;
  background: #fff;
  border: 1px solid #e8eaed;
  transition:
    color 0.2s ease,
    border-color 0.2s ease,
    transform 0.2s ease;

  &:hover {
    color: var(--primary-color, #7c3aed);
    border-color: color-mix(in srgb, var(--primary-color, #8b5cf6) 35%, #e8eaed);
    transform: translateY(-2px);
  }

  :deep(svg) {
    width: 18px;
    height: 18px;
  }
}

.site-showcase__footer-qr-row {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 360px;
}

.site-showcase__footer-qr-wrap {
  flex-shrink: 0;
  width: 88px;
  height: 88px;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  border: 1px solid #e8eaed;
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.site-showcase__footer-qr-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.site-showcase__footer-qr-text {
  min-width: 0;
}

.site-showcase__footer-qr-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  color: #202124;
  line-height: 1.4;
}

.site-showcase__footer-qr-sub {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  color: #80868b;
}

.site-showcase__footer-nav {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(16px, 3vw, 32px);
}

.site-showcase__footer-col-title {
  margin: 0 0 14px;
  font-size: 14px;
  font-weight: 600;
  color: #202124;
  letter-spacing: 0.02em;
}

.site-showcase__footer-links {
  margin: 0;
  padding: 0;
  list-style: none;
}

.site-showcase__footer-links li {
  margin-bottom: 10px;

  &:last-child {
    margin-bottom: 0;
  }
}

.site-showcase__footer-link {
  font-size: 13px;
  line-height: 1.5;
  color: #5f6368;
  text-decoration: none;
  transition: color 0.2s ease;

  &:hover {
    color: var(--primary-color, #7c3aed);
  }
}

.site-showcase__footer-contact-bar {
  padding: 20px 0 8px;
  margin-bottom: 4px;
  border-top: 1px solid #e0e3e7;
}

.site-showcase__footer-contact-title {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 600;
  color: #202124;
  letter-spacing: 0.02em;
}

.site-showcase__footer-contact-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 12px 28px;
  align-items: baseline;
}

.site-showcase__footer-contact-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 8px;
  font-size: 13px;
  line-height: 1.5;
}

.site-showcase__footer-contact-label {
  color: #80868b;
  flex-shrink: 0;
}

.site-showcase__footer-contact-value {
  color: #3c4043;
  text-decoration: none;
  transition: color 0.2s ease;

  &:hover {
    color: var(--primary-color, #7c3aed);
  }

  &--plain {
    color: #202124;
    font-weight: 500;

    &:hover {
      color: #202124;
    }
  }
}

@media (max-width: 520px) {
  .site-showcase__footer-contact-list {
    flex-direction: column;
    gap: 10px;
  }
}

.site-showcase__footer-legal {
  padding: 16px 0 24px;
  border-top: 1px solid #e0e3e7;
}

.site-showcase__footer-legal-text {
  margin: 0;
  text-align: center;
  font-size: 12px;
  line-height: 1.65;
  color: #80868b;
}

@media (max-width: 900px) {
  .site-showcase__footer-main {
    grid-template-columns: 1fr;
  }

  .site-showcase__footer-brand {
    text-align: center;
  }

  .site-showcase__footer-slogan {
    margin-left: auto;
    margin-right: auto;
  }

  .site-showcase__footer-social {
    justify-content: center;
  }

  .site-showcase__footer-qr-row {
    margin: 0 auto;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .site-showcase__footer-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .site-showcase__footer-nav {
    grid-template-columns: 1fr;
  }
}
</style>
