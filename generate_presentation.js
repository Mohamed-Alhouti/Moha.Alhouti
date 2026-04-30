const pptxgen = require('pptxgenjs');
const {
  imageSizingCrop,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require('/home/oai/skills/slides/pptxgenjs_helpers');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'AquaSmart SEWA Demo';
pptx.subject = 'Smart Water Monitoring and Leak Detection Demo';
pptx.title = 'AquaSmart SEWA Executive Pitch';
pptx.company = 'SEWA';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Arial',
  bodyFontFace: 'Arial',
  lang: 'en-US'
};
pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';

const W = 13.333, H = 7.5;
const navy = '031426';
const blue = '0B5CAD';
const cyan = '32CFFF';
const white = 'F8FBFF';
const soft = 'A8DDFE';
const green = '2BE887';
const amber = 'FFC226';
const red = 'FF3838';
const logoPath = '/mnt/data/aquasmart_production_demo/sewa_logo.png';
const dashboardPath = '/mnt/data/a_wide_high_res_screenshot_of_a_dark_blue_themed.png';

function bg(slide) {
  slide.background = { color: navy };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:W, h:.12, fill:{color:cyan, transparency:20}, line:{color:cyan, transparency:100} });
}
function title(slide, t, st) {
  slide.addText(t, { x:.55, y:.45, w:8.2, h:.45, fontFace:'Arial', fontSize:28, bold:true, color:white, margin:0 });
  if (st) slide.addText(st, { x:.58, y:.95, w:9.5, h:.32, fontSize:12.5, color:soft, margin:0 });
  slide.addImage({ path: logoPath, x:10.85, y:.28, w:1.95, h:.65 });
}
function pill(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h:.34, rectRadius:.08, fill:{color, transparency:12}, line:{color, transparency:35} });
  slide.addText(text, { x:x+.08, y:y+.07, w:w-.16, h:.18, fontSize:9.5, bold:true, color:white, align:'center', margin:0 });
}
function card(slide, x, y, w, h, label, value, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius:.08, fill:{color:'082A4E', transparency:8}, line:{color:'217DBC', transparency:28} });
  slide.addText(label, { x:x+.18, y:y+.18, w:w-.36, h:.22, fontSize:10, bold:true, color:soft, margin:0 });
  slide.addText(value, { x:x+.18, y:y+.56, w:w-.36, h:.42, fontSize:23, bold:true, color:color || white, margin:0 });
}
function bullets(slide, items, x, y, w, fs=15) {
  items.forEach((it, idx) => {
    slide.addText('• ' + it, { x, y: y + idx * 0.58, w, h: .32, fontSize: fs, color:white, margin:0, fit:'shrink' });
  });
}
function footer(slide) {
  slide.addText('AquaSmart SEWA | Smart Water Monitoring System | Synthetic demo for innovation discussion', { x:.55, y:7.12, w:10.5, h:.22, fontSize:8.5, color:'7FBDE8', margin:0 });
}
function check(slide) {
  warnIfSlideHasOverlaps(slide, pptx, { ignoreDecorativeShapes: true });
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

// Slide 1
let slide = pptx.addSlide(); bg(slide);
slide.addImage({ path: logoPath, x:.55, y:.4, w:2.45, h:.9 });
slide.addText('AquaSmart SEWA', { x:.75, y:2.0, w:7.5, h:.7, fontSize:40, bold:true, color:white, margin:0 });
slide.addText('Production-Level Demo for Smart Water Monitoring, Leak Detection and Predictive Alerts', { x:.8, y:2.85, w:7.8, h:.42, fontSize:17, color:cyan, margin:0 });
slide.addText('Transforming SCADA data into operational intelligence for Khorfakkan water distribution zones.', { x:.82, y:3.48, w:7.4, h:.35, fontSize:13.5, color:soft, margin:0 });
pill(slide, 'SCADA + AI/IoT + GIS + Business Value', .82, 4.15, 3.2, blue);
pill(slide, 'Synthetic demo data', 4.25, 4.15, 2.0, '14395F');
slide.addShape(pptx.ShapeType.arc, { x:9.0, y:1.35, w:3.1, h:3.1, line:{color:cyan, transparency:15, width:3}, adjustPoint:.25 });
slide.addText('💧', { x:9.72, y:1.95, w:1.5, h:1.2, fontSize:66, margin:0, align:'center' });
slide.addText('Prepared for executive review', { x:.82, y:6.38, w:4, h:.22, fontSize:10.5, color:'B4DCF7', margin:0 });
footer(slide); check(slide);

// Slide 2 Problem
slide = pptx.addSlide(); bg(slide); title(slide, 'Operational Challenge', 'Water networks already generate data, but response is still often reactive.');
card(slide, .65, 1.65, 2.5, 1.3, 'NRW losses', 'Water loss', red);
card(slide, 3.45, 1.65, 2.5, 1.3, 'Leak detection', 'Reactive', amber);
card(slide, 6.25, 1.65, 2.5, 1.3, 'SCADA data', 'Underused', cyan);
card(slide, 9.05, 1.65, 2.5, 1.3, 'Field response', 'Delayed', amber);
bullets(slide, [
  'Flow, pressure and consumption readings may indicate abnormal behavior before customers report an issue.',
  'Without zone-level analytics, teams spend time confirming the problem instead of acting on it.',
  'The demo shows how existing SCADA-like data can be converted into a prioritized control room workflow.'
], .85, 3.65, 10.8, 16);
footer(slide); check(slide);

// Slide 3 Dashboard screenshot
slide = pptx.addSlide(); bg(slide); title(slide, 'Control Room Dashboard', 'A SEWA-style interface for monitoring, alerts, GIS zones and business KPIs.');
slide.addImage({ path: dashboardPath, ...imageSizingCrop(dashboardPath, .55, 1.35, 12.2, 5.35) });
footer(slide); check(slide);

// Slide 4 architecture
slide = pptx.addSlide(); bg(slide); title(slide, 'Production-Level Demo Architecture', 'Simple enough for a prototype, but structured like a real product.');
const steps = [
  ['SCADA Data', 'Flow, pressure, consumption and timestamps'],
  ['Analytics Engine', 'Rules and anomaly scoring'],
  ['GIS Dashboard', 'Khorfakkan zones and risk view'],
  ['Alarm Workflow', 'Critical and warning alerts'],
  ['Business Value', 'NRW, efficiency and savings']
];
steps.forEach((s,i)=>{
  const x=.65+i*2.45;
  slide.addShape(pptx.ShapeType.roundRect, { x, y:2.1, w:2.05, h:1.25, rectRadius:.08, fill:{color:'082A4E'}, line:{color:'28B7FF', transparency:20} });
  slide.addText(s[0], { x:x+.14, y:2.32, w:1.78, h:.25, fontSize:13, bold:true, color:white, align:'center', margin:0 });
  slide.addText(s[1], { x:x+.14, y:2.75, w:1.78, h:.38, fontSize:8.6, color:soft, align:'center', fit:'shrink', margin:0 });
  if(i<steps.length-1) slide.addText('→', { x:x+2.08, y:2.45, w:.35, h:.3, fontSize:20, bold:true, color:cyan, margin:0 });
});
bullets(slide, [
  'Synthetic data generator creates repeatable SCADA-style patterns for demos and training.',
  'Transparent leak logic combines pressure drop, abnormal flow and leakage probability.',
  'GIS map gives a local Khorfakkan view: Zubara, Mussala, Hayawa, Al Luluyah and Al Wurrayah.',
  'Export options support CSV snapshots and executive reporting.'
], .85, 4.35, 11.1, 14.5);
footer(slide); check(slide);

// Slide 5 Features
slide = pptx.addSlide(); bg(slide); title(slide, 'What Was Upgraded', 'The demo now behaves more like a working SCADA innovation prototype.');
const feats = [
  ['🔔', 'Blinking SCADA-style alarms', 'Critical and warning cards pulse to demand operator attention.'],
  ['🗺️', 'Interactive GIS-style map', 'Local zone markers and risk colors are displayed on a dark basemap.'],
  ['📱', 'Mobile field view', 'Simplified zone cards for technicians and response teams.'],
  ['📊', 'Executive reporting', 'PowerPoint and CSV exports support review and stakeholder sharing.']
];
feats.forEach((f,i)=>{
  const x = i%2 === 0 ? .75 : 6.75; const y = i<2 ? 1.75 : 4.15;
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w:5.25, h:1.55, rectRadius:.08, fill:{color:'082A4E'}, line:{color:'247FC3', transparency:25} });
  slide.addText(f[0], { x:x+.2, y:y+.28, w:.55, h:.55, fontSize:26, margin:0 });
  slide.addText(f[1], { x:x+.9, y:y+.28, w:4.0, h:.25, fontSize:15, bold:true, color:white, margin:0 });
  slide.addText(f[2], { x:x+.9, y:y+.72, w:4.0, h:.42, fontSize:11, color:soft, margin:0, fit:'shrink' });
});
footer(slide); check(slide);

// Slide 6 KPIs
slide = pptx.addSlide(); bg(slide); title(slide, 'Business Value Simulation', 'The dashboard does not only display data. It translates data into value.');
card(slide, .8, 1.65, 2.35, 1.35, 'NRW Loss', '28.6% → 21.4%', green);
card(slide, 3.55, 1.65, 2.35, 1.35, 'Response Time', '4.2h → 1.8h', green);
card(slide, 6.3, 1.65, 2.35, 1.35, 'Efficiency', '68% → 79%', green);
card(slide, 9.05, 1.65, 2.35, 1.35, 'Savings', 'AED 1.6M', green);
bullets(slide, [
  'Earlier detection reduces water loss duration and helps prioritize emergency response.',
  'Zone-level visibility supports maintenance planning, budgeting and performance review.',
  'Business metrics are mock values in the prototype, but the logic is ready for calibration using real data.'
], 1.0, 4.0, 10.6, 15.5);
footer(slide); check(slide);

// Slide 7 Roadmap
slide = pptx.addSlide(); bg(slide); title(slide, 'Suggested Implementation Roadmap', 'A phased route from demo to operational pilot.');
const phases = [
  ['Phase 1', 'Pilot demo', 'Validate dashboard logic using exported SCADA history.'],
  ['Phase 2', 'Data integration', 'Connect approved SCADA feeds and define data quality rules.'],
  ['Phase 3', 'Field workflow', 'Link alarms to field response and close-out records.'],
  ['Phase 4', 'AI optimization', 'Train models with confirmed leaks and hydraulic context.']
];
phases.forEach((p,i)=>{
  const y = 1.55 + i*1.28;
  slide.addShape(pptx.ShapeType.roundRect, { x:1.0, y, w:1.45, h:.56, rectRadius:.06, fill:{color:blue}, line:{color:cyan, transparency:55} });
  slide.addText(p[0], { x:1.13, y:y+.16, w:1.18, h:.16, fontSize:10, bold:true, color:white, align:'center', margin:0 });
  slide.addText(p[1], { x:2.8, y:y+.04, w:2.6, h:.24, fontSize:15, bold:true, color:white, margin:0 });
  slide.addText(p[2], { x:5.55, y:y+.06, w:5.8, h:.32, fontSize:12, color:soft, margin:0 });
});
footer(slide); check(slide);

// Slide 8 Close
slide = pptx.addSlide(); bg(slide);
slide.addImage({ path: logoPath, x:.7, y:.5, w:2.45, h:.9 });
slide.addText('AquaSmart SEWA enables proactive water management using data SEWA already has.', { x:.9, y:2.0, w:10.6, h:1.0, fontSize:30, bold:true, color:white, margin:0, fit:'shrink' });
slide.addText('The next practical step is a controlled Khorfakkan pilot using selected SCADA points and field-confirmed leak events.', { x:.92, y:3.35, w:9.8, h:.55, fontSize:16, color:cyan, margin:0 });
pill(slide, 'Proactive operations', .95, 4.45, 2.05, blue);
pill(slide, 'NRW reduction', 3.25, 4.45, 1.65, '14395F');
pill(slide, 'Faster response', 5.15, 4.45, 1.65, '14395F');
pill(slide, 'Better planning', 7.05, 4.45, 1.65, '14395F');
footer(slide); check(slide);

pptx.writeFile({ fileName: '/mnt/data/aquasmart_production_demo/AquaSmart_SEWA_Executive_Pitch.pptx' });
