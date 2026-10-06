import en from '../locales/en/common.json'
import fa from '../locales/fa/common.json'

type Locale = 'en' | 'fa'
type Tree = { [key: string]: string | Tree }

const translations: Record<Locale, Tree> = { en: en as Tree, fa: fa as Tree }

const saved = typeof window !== 'undefined' ? localStorage.getItem('locale') : null
let currentLocale: Locale = saved === 'en' ? 'en' : 'fa'

export function setLocale(locale: Locale) {
  currentLocale = locale
  if (typeof window !== 'undefined') {
    localStorage.setItem('locale', locale)
    document.documentElement.lang = locale
    document.documentElement.dir = locale === 'fa' ? 'rtl' : 'ltr'
  }
}

export function getLocale(): Locale {
  return currentLocale
}

/** Look up a dotted key; unknown keys fall back to the English tree and finally to the key itself. */
export function t(key: string): string {
  for (const tree of [translations[currentLocale], translations.en]) {
    let node: string | Tree | undefined = tree
    for (const part of key.split('.')) {
      node = typeof node === 'object' ? node[part] : undefined
    }
    if (typeof node === 'string') return node
  }
  return key
}
