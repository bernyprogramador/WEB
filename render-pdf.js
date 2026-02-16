const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });

  try {
    const page = await browser.newPage();
    const filePath = path.join(__dirname, 'index.html');
    const fileUrl = `file://${filePath}`;

    await page.goto(fileUrl, { waitUntil: 'networkidle' });

    await page.pdf({
      path: path.join(__dirname, 'menu.pdf'),
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true
    });

    console.log('PDF generado correctamente: menu.pdf');
  } catch (error) {
    console.error('Error al generar el PDF:', error);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
