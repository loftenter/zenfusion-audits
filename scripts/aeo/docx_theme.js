/**
 * ZENFUSION DOCX THEME — shared styling helpers for Market Analysis and
 * Competitive Analysis Word deliverables.
 *
 * Usage:
 *   const { theme, h1, h2, h3, body, bullet, spacer, pb, callout,
 *           dataTable, coverPage, buildDoc } = require('./docx_theme.js')(paletteObj);
 *
 * paletteObj comes straight from the client's config.json → brand_palette,
 * e.g. { green:"35EEA0", blue:"30C8EE", navy:"041952", charcoal:"1A1A1A" }.
 * Pass an optional second arg { accent: "0072B5" } to override the accent
 * color used for H2 headings / callout borders (e.g. a client-specific
 * "authority" color instead of the default Zenfusion blue) — see the
 * Watergen/WGP report, which used a teal accent instead of house blue.
 *
 * This module ONLY carries styling. Content (research, prose, numbers) is
 * always agent-written per client — never templated — per the honesty
 * rules in brain.md.
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, LevelFormat, WidthType, BorderStyle,
  ShadingType, PageBreak, Header, Footer, PageNumber, NumberFormat
} = require('docx');

module.exports = function (palette, opts) {
  palette = palette || { green: "35EEA0", blue: "30C8EE", navy: "041952", charcoal: "1A1A1A" };
  opts = opts || {};

  const NAVY  = palette.navy    || "041952";
  const ACCENT = opts.accent    || palette.blue || "30C8EE";
  const CHAR  = palette.charcoal || "1A1A1A";
  const WHITE = "FFFFFF";
  const LGRAY = "F5F7FA";

  const bdr  = (c = "CCCCCC") => ({ style: BorderStyle.SINGLE, size: 1, color: c });
  const bdrs = (c = "CCCCCC") => ({ top: bdr(c), bottom: bdr(c), left: bdr(c), right: bdr(c) });

  function h1(text) {
    return new Paragraph({
      heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 },
      children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: NAVY })]
    });
  }
  function h2(text) {
    return new Paragraph({
      heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 120 },
      children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: ACCENT })]
    });
  }
  function h3(text) {
    return new Paragraph({
      heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 80 },
      children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: CHAR })]
    });
  }
  function body(text, runOpts) {
    runOpts = runOpts || {};
    return new Paragraph({
      spacing: { before: 80, after: 120 },
      children: [new TextRun({ text, font: "Arial", size: 20, color: CHAR, ...runOpts })]
    });
  }
  function bullet(text, label) {
    const children = label
      ? [new TextRun({ text: label + " ", font: "Arial", size: 20, bold: true, color: ACCENT }),
         new TextRun({ text, font: "Arial", size: 20, color: CHAR })]
      : [new TextRun({ text, font: "Arial", size: 20, color: CHAR })];
    return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { before: 40, after: 60 }, children });
  }
  function spacer() { return new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun("")] }); }
  function pb() { return new Paragraph({ children: [new PageBreak()] }); }

  // Callout box (e.g. "HEADLINE NUMBERS", "THE CORE OPPORTUNITY"). Color
  // defaults to the accent; pass a different hex + light fill for variants.
  function callout(label, text, borderColor, fillColor) {
    borderColor = borderColor || ACCENT;
    fillColor = fillColor || "EEF6FB";
    return new Table({
      width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
      rows: [new TableRow({
        children: [new TableCell({
          borders: {
            top: { style: BorderStyle.SINGLE, size: 6, color: borderColor }, bottom: bdr("DDDDDD"),
            left: { style: BorderStyle.SINGLE, size: 6, color: borderColor }, right: bdr("DDDDDD")
          },
          shading: { fill: fillColor, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 160, right: 160 },
          width: { size: 9360, type: WidthType.DXA },
          children: [
            new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: label, font: "Arial", size: 18, bold: true, color: NAVY, allCaps: true })] }),
            new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text, font: "Arial", size: 20, color: CHAR })] })
          ]
        })]
      })]
    });
  }

  // Generic data table — headers[] + rows[][] + optional colWidths[] (DXA,
  // must sum to 9360). Header row = navy fill/white text; body rows
  // alternate LGRAY/white. Used for stat tables, competitor tables, threat
  // rankings, cluster breakdowns — anything tabular.
  function dataTable(headers, rows, colWidths) {
    const n = headers.length;
    const ws = colWidths || Array(n).fill(Math.floor(9360 / n));
    const hdr = new TableRow({
      children: headers.map((hcell, i) => new TableCell({
        borders: bdrs(NAVY), shading: { fill: NAVY, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 100 },
        width: { size: ws[i], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: String(hcell), font: "Arial", size: 17, bold: true, color: WHITE })] })]
      })), tableHeader: true
    });
    const dataRows = rows.map((r, i) => new TableRow({
      children: r.map((cell, j) => new TableCell({
        borders: bdrs("CCCCCC"), shading: { fill: i % 2 === 0 ? LGRAY : WHITE, type: ShadingType.CLEAR },
        margins: { top: 70, bottom: 70, left: 120, right: 100 },
        width: { size: ws[j], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: String(cell), font: "Arial", size: 17, color: CHAR })] })]
      }))
    }));
    return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: ws, rows: [hdr, ...dataRows] });
  }

  // Cover page block. domainLine/scopeLine are optional secondary lines
  // (e.g. "qualitywatertreatment.com/collections/waterdrop-filter" or
  // "Core Keyword: Line Set  |  United States  |  July 2026").
  function coverPage({ clientName, docTitle, scopeLine, dateLine, preparedBy }) {
    preparedBy = preparedBy || "Prepared by Zenfusion  |  Confidential";
    const children = [
      new Paragraph({ spacing: { before: 1440, after: 120 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: clientName, font: "Arial", size: 48, bold: true, color: ACCENT })] }),
      new Paragraph({ spacing: { before: 0, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: docTitle, font: "Arial", size: 34, bold: true, color: NAVY })] }),
    ];
    if (scopeLine) children.push(new Paragraph({ spacing: { before: 0, after: 80 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: scopeLine, font: "Arial", size: 20, bold: true, color: ACCENT })] }));
    if (dateLine) children.push(new Paragraph({ spacing: { before: 0, after: 80 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: dateLine, font: "Arial", size: 22, color: CHAR })] }));
    children.push(new Paragraph({ spacing: { before: 0, after: 1440 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: preparedBy, font: "Arial", size: 20, color: "888888", italics: true })] }));
    children.push(pb());
    return children;
  }

  // Header/footer with page numbers — satisfies the standing "polished
  // deliverable" preference (title page, styled tables, header/footer with
  // page numbers) for every Market Analysis / Competitive Analysis doc.
  function pageFooter(reportLabel) {
    return new Footer({
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: (reportLabel ? reportLabel + "   |   " : ""), font: "Arial", size: 14, color: "888888" }),
          new TextRun({ text: "Page ", font: "Arial", size: 14, color: "888888" }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 14, color: "888888" }),
          new TextRun({ text: " of ", font: "Arial", size: 14, color: "888888" }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 14, color: "888888" }),
        ]
      })]
    });
  }
  function pageHeader(text) {
    return new Header({
      children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: text || "", font: "Arial", size: 14, color: "AAAAAA", allCaps: true })]
      })]
    });
  }

  // Assemble the final Document. `children` is the flat array of
  // Paragraphs/Tables built with the helpers above (cover + sections).
  function buildDoc(children, { headerText, footerLabel } = {}) {
    return new Document({
      numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
      styles: {
        default: { document: { run: { font: "Arial", size: 20 } } },
        paragraphStyles: [
          { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: "Arial", color: NAVY }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
          { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: "Arial", color: ACCENT }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
          { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: "Arial", color: CHAR }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
        ]
      },
      sections: [{
        properties: {
          page: {
            size: { width: 12240, height: 15840 },
            margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 },
            pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL }
          }
        },
        headers: { default: pageHeader(headerText) },
        footers: { default: pageFooter(footerLabel) },
        children
      }]
    });
  }

  return { theme: { NAVY, ACCENT, CHAR, WHITE, LGRAY }, h1, h2, h3, body, bullet, spacer, pb, callout, dataTable, coverPage, buildDoc, Packer };
};
