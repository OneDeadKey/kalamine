import { getSupportedChars, analyzeKeyboardLayout } from './layout-analyzer.js';

window.addEventListener('DOMContentLoaded', () => {
  const inputField = document.querySelector('input');
  const keyboard   = document.querySelector('x-keyboard');

  const headingColor = 'rgb(127, 127, 127)'; // getComputedStyle(document.querySelector('h3')).color;

  let corpus = {};
  let keyChars = {};
  let impreciseData = false;

  // display a percentage value
  const fmtPercent = (num, p) => `${Math.round(10 ** p * num) / 10 ** p}%`;
  const showPercent = (sel, num, precision) => {
    document.querySelector(sel).innerText = fmtPercent(num, precision);
  };
  const showPercentAll = (sel, nums, precision) => {
    document.querySelector(sel).innerText =
      nums.map(value => fmtPercent(value, precision)).join(' / ');
  };

  const showNGrams = (ngrams) => {
    const sum = dict => Object.entries(dict).reduce((acc, [_, e]) => acc + e, 0);

    showPercent('#sfu-total',        sum(ngrams.sfb),         2);
    showPercent('#sku-total',        sum(ngrams.skb),         2);

    showPercent('#sfu-all',          sum(ngrams.sfb),         2);
    showPercent('#extensions-all',   sum(ngrams.lsb),         2);
    showPercent('#scissors-all',     sum(ngrams.scissor),     2);

    showPercent('#inward-all',       sum(ngrams.inwardRoll),  1);
    showPercent('#outward-all',      sum(ngrams.outwardRoll), 1);
    showPercent('#sku-all',          sum(ngrams.skb),         2);

    showPercent('#sks-all',          sum(ngrams.sks),         1);
    showPercent('#sfs-all',          sum(ngrams.sfs),         1);
    showPercent('#redirect-all',     sum(ngrams.redirect),    1);
    showPercent('#bad-redirect-all', sum(ngrams.badRedirect), 2);

    const bottlenecks = document.querySelector('#bottlenecks stats-table');
    bottlenecks.updateTableData('#sfu-bigrams',    ngrams.sfb,         2);
    bottlenecks.updateTableData('#extended-rolls', ngrams.lsb,         2);
    bottlenecks.updateTableData('#scissors',       ngrams.scissor,     2);

    const bigrams = document.querySelector('#bigrams stats-table');
    bigrams.updateTableData('#sku-bigrams',       ngrams.skb,         2);
    bigrams.updateTableData('#inward',            ngrams.inwardRoll,  2);
    bigrams.updateTableData('#outward',           ngrams.outwardRoll, 2);

    const trigrams = document.querySelector('#trigrams stats-table');
    trigrams.updateTableData('#sks',              ngrams.sks,         2);
    trigrams.updateTableData('#sfs',              ngrams.sfs,         2);
    trigrams.updateTableData('#redirect',         ngrams.redirect,    2);
    trigrams.updateTableData('#bad-redirect',     ngrams.badRedirect, 2);
  };

  const showReport = () => {
    keyChars = getSupportedChars(keyboard.layout.keyMap, keyboard.layout.deadKeys);
    const report = analyzeKeyboardLayout(keyboard, corpus, keyChars, headingColor);
    console.log(corpus);
    console.log(report);

    document.querySelector('#sfu stats-canvas').renderData({
      values: report.totalSfuSkuPerFinger,
      maxValue: 4,
      precision: 2,
      flipVertically: true,
      detailedValues: true,
    });

    document.querySelector('#load stats-canvas').renderData({
      values: report.loadGroups,
      maxValue: 25,
      precision: 1
    });

    const sumUpBar = bar => bar.good + bar.meh + bar.bad;
    const sumUpBarGroup = group => group.reduce((acc, bar) => acc + sumUpBar(bar), 0);

    showPercentAll('#load small', report.loadGroups.map(sumUpBarGroup), 1);
    showPercent('#unsupported-all', report.totalUnsupportedChars, 3);

    document.querySelector('#imprecise-data').hidden = !impreciseData;

    document
      .querySelector('#bottlenecks stats-table')
      .updateTableData('#unsupported', report.unsupportedChars, 3);

    showNGrams(report.ngrams);
  };

  document
    .getElementById('corpus')
    .addEventListener('change', event => {
      fetch(`corpus/${event.target.value}.json`)
        .then(response => response.json())
        .then(data => {
          corpus = data;
          document.getElementById('analyzer').hidden = false;
          showReport();
        });
    });
});
