/* Japanese line breaks: never split a word or phrase across lines (e.g. 公|開しました).
   Chrome/Edge do this in CSS (word-break: auto-phrase, see nd-base.css). Other browsers (Safari, Firefox)
   get Google's BudouX phrase splitter, which marks phrase boundaries so lines only wrap between phrases. */
if (!CSS.supports('word-break', 'auto-phrase')) {
  const SEL = 'h1, h2, h3, h4, p, li, dt, dd, summary, figcaption, blockquote, .btn, .nd-viewer__btn, .eyebrow, .tone__tab';
  const JA = /[぀-ヿ㐀-鿿]/;
  const run = async () => {
    const els = [...document.querySelectorAll(SEL)].filter((el) => !el.closest('[data-no-budoux], script, style, textarea') && JA.test(el.textContent) && !el.querySelector(SEL));
    if (!els.length) return;
    const { loadDefaultJapaneseParser } = await import('https://cdn.jsdelivr.net/npm/budoux@0.7.0/+esm');
    const parser = loadDefaultJapaneseParser();
    els.forEach((el) => { try { parser.applyToElement(el); } catch (e) { /* leave the element as it is */ } });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, { once: true }); else run();
}
