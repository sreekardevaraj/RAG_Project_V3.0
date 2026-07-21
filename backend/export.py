from fpdf import FPDF
import os
from datetime import datetime


class ChatExporter(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(79, 70, 229)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "RAG Chatbot V2 - Chat Export", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")


def export_chat_to_pdf(messages: list, output_path: str) -> str:
    pdf = ChatExporter()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Exported on {datetime.now().strftime('%B %d, %Y at %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    for msg in messages:
        role    = msg.get("role", "")
        content = msg.get("content", "")
        source  = msg.get("source", "")
        details = msg.get("details", [])

        if role == "user":
            pdf.set_fill_color(237, 233, 254)
            pdf.set_text_color(79, 70, 229)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 8, "  You", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 46)
            pdf.set_fill_color(245, 243, 255)
            safe = content.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, f"  {safe}", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

        elif role == "assistant":
            color_map = {
                "PDF":     (5, 150, 105),
                "Web":     (37, 99, 235),
                "Chat":    (217, 119, 6),
                "Analyst": (124, 58, 237),
            }
            label_map = {
                "PDF": "  PDF Source", "Web": "  Web Source",
                "Chat": "  Chat", "Analyst": "  Analyst"
            }
            r, g, b = color_map.get(source, (100, 100, 100))
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(40, 7, label_map.get(source, "  Assistant"), fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 46)
            pdf.set_fill_color(248, 250, 252)
            safe = content.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, f"  {safe}", fill=True, new_x="LMARGIN", new_y="NEXT")

            if details:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 6, "  References:", new_x="LMARGIN", new_y="NEXT")
                for item in details:
                    if source == "PDF":
                        ref = f"    Page {item.get('page','?')} | {os.path.basename(str(item.get('source','?')))}"
                    else:
                        ref = f"    {item.get('title','')} -> {item.get('url','')}"
                    safe_ref = ref.encode("latin-1", "replace").decode("latin-1")
                    pdf.multi_cell(0, 6, safe_ref, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    pdf.output(output_path)
    print(f"[Export] Chat exported to: {output_path}")
    return output_path