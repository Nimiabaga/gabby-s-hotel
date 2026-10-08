const fs = require('fs');
const path = require('path');

const PRICES = JSON.parse(fs.readFileSync(path.join(__dirname, 'prices.json'), 'utf8'));

function findPriceLine(lines, startIdx) {
  const priceRe = /₦\s*[\d,]+/;
  for (let i = startIdx; i < Math.min(lines.length, startIdx + 5); i++) {
    if (priceRe.test(lines[i])) return i;
  }
  return null;
}

function replacePriceInLine(line, newPrice) {
  const priceRe = /₦\s*[\d,]+/;
  if (priceRe.test(line)) return line.replace(priceRe, newPrice);
  if (line.includes('</p>')) return line.replace('</p>', `${newPrice}</p>`);
  return line;
}

function run() {
  const root = process.cwd();
  const files = fs.readdirSync(root).filter(f => f.endsWith('.html'));
  const changed = [];
  const updatedItems = new Set();
  const notFound = new Set(Object.keys(PRICES));

  for (const file of files) {
    const fp = path.join(root, file);
    const text = fs.readFileSync(fp, 'utf8');
    const lines = text.split(/\r?\n/);
    let modified = false;

    for (const [item, newPrice] of Object.entries(PRICES)) {
      const re = new RegExp(item.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
      for (let i = 0; i < lines.length; i++) {
        if (re.test(lines[i])) {
          const pidx = findPriceLine(lines, i);
          if (pidx !== null) {
            const old = lines[pidx];
            const nw = replacePriceInLine(old, newPrice);
            if (nw !== old) {
              lines[pidx] = nw; modified = true; updatedItems.add(item); notFound.delete(item);
            }
          } else {
            if (lines[i].includes('<p') && lines[i].includes('</p>')) {
              const nw = replacePriceInLine(lines[i], newPrice);
              if (nw !== lines[i]) { lines[i] = nw; modified = true; updatedItems.add(item); notFound.delete(item); }
            }
          }
        }
      }
    }

    if (modified) {
      fs.writeFileSync(fp, lines.join('\n'), 'utf8');
      changed.push(file);
    }
  }

  console.log('Updated files:');
  changed.forEach(f => console.log(' -', f));
  console.log('\nUpdated items count:', updatedItems.size);
  if (notFound.size) {
    console.log('\nItems not found:');
    for (const it of notFound) console.log(' -', it);
  }
}

run();
