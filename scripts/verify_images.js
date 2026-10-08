const fs = require('fs');
const path = require('path');

const IMAGES_DIR = path.join(__dirname, '..', 'images');
const ROOT = path.join(__dirname, '..');

function formatNaira(n) {
  return '₦' + Number(n).toLocaleString('en-US');
}

function findPriceNear(lines, idx) {
  const priceRe = /₦\s*[\d,]+/;
  // search nearby lines
  const start = Math.max(0, idx - 6);
  const end = Math.min(lines.length, idx + 6);
  for (let i = start; i < end; i++) {
    const m = lines[i].match(priceRe);
    if (m) return m[0];
  }
  return null;
}

function scan() {
  const images = fs.readdirSync(IMAGES_DIR).filter(f => /\.(jpg|jpeg|png)$/i.test(f));
  const htmlFiles = fs.readdirSync(ROOT).filter(f => f.endsWith('.html'));
  const report = [];

  for (const img of images) {
    // try to parse trailing price from filename: -<digits>
    const m = img.match(/-(\d{3,})(?:\.|$)/);
    const imgPath = path.join('images', img);
    const entry = { image: imgPath, parsedPrice: null, found: [] };
    if (m) entry.parsedPrice = formatNaira(m[1]);

    for (const hf of htmlFiles) {
      const content = fs.readFileSync(path.join(ROOT, hf), 'utf8');
      const lines = content.split(/\r?\n/);
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(imgPath) || lines[i].includes(img) ) {
          const price = findPriceNear(lines, i);
          // also try to find a nearby item name
          let name = null;
          // look for h4 or p.item within range
          for (let j = Math.max(0, i - 6); j < Math.min(lines.length, i + 6); j++) {
            const h4 = lines[j].match(/<h4[^>]*>([^<]+)<\/h4>/i);
            if (h4) { name = h4[1].trim(); break; }
            const p = lines[j].match(/<p[^>]*class="item[^"]*"[^>]*>([^<]+)<\/p>/i);
            if (p) { name = p[1].trim(); break; }
          }
          entry.found.push({ file: hf, line: i + 1, price: price, name: name });
        }
      }
    }
    report.push(entry);
  }

  // print concise report
  const mismatches = [];
  console.log('Image verification report:');
  for (const r of report) {
    if (r.parsedPrice === null && r.found.length === 0) continue; // ignore unrelated images
    console.log('\n- ' + r.image + (r.parsedPrice ? (' (filename price ' + r.parsedPrice + ')') : ''));
    if (r.found.length === 0) {
      console.log('  Not referenced in any HTML files.');
      continue;
    }
    for (const f of r.found) {
      console.log(`  Referenced in ${f.file} (line ${f.line}) — item: ${f.name || 'N/A'} — price: ${f.price || 'N/A'}`);
      if (r.parsedPrice && f.price && r.parsedPrice !== f.price) {
        mismatches.push({ image: r.image, file: f.file, imagePrice: r.parsedPrice, htmlPrice: f.price, name: f.name });
      }
    }
  }

  console.log('\nSummary: ' + mismatches.length + ' mismatches found.');
  if (mismatches.length) {
    console.log('\nMismatches:');
    mismatches.forEach(m => {
      console.log(` - ${m.image} referenced in ${m.file}: image=${m.imagePrice} html=${m.htmlPrice} item=${m.name}`);
    });
  }
}

scan();
