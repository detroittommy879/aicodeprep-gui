"""
Add translations to .ts files.

This script adds Spanish, Chinese Simplified, and French translations to the
generated .ts files.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

# Translation dictionaries
TRANSLATIONS = {
    'es': {  # Spanish
        'aicodeprep-gui - File Selection': 'aicodeprep-gui - Selección de archivos',
        '&File': '&Archivo',
        '&Quit': '&Salir',
        '&Edit': '&Editar',
        '&New Preset…': '&Nuevo ajuste predefinido…',
        'Open Settings Folder…': 'Abrir carpeta de configuración…',
        '&Language / Idioma / 语言…': '&Idioma / Language / 语言…',
        '&Flow': '&Flujo',
        'Import Flow JSON…': 'Importar JSON de flujo…',
        'Export Flow JSON…': 'Exportar JSON de flujo…',
        'Reset to Default Flow': 'Restaurar flujo predeterminado',
        '&Help': 'Ay&uda',
        'Help / Links and Guides': 'Ayuda / Enlaces y guías',
        '&About': '&Acerca de',
        'Send Ideas, bugs, thoughts!': '¡Enviar ideas, errores, pensamientos!',
        'Activate Pro…': 'Activar Pro…',
        '&Debug': '&Depurar',
        'Take Screenshot': 'Tomar captura de pantalla',
        'Current Language Info': 'Información del idioma actual',
        'Accessibility Check': 'Verificación de accesibilidad',
        '&Output format:': '&Formato de salida:',
        'Estimated tokens: 0': 'Tokens estimados: 0',
        'The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into your AI assistant.': 'Los archivos seleccionados se agregarán al bloque de contexto LLM junto con su instrucción, se escribirán en fullcode.txt y se copiarán al portapapeles, listos para pegar en su asistente de IA.',
        'Prompt Preset Buttons:': 'Botones de ajustes predefinidos:',
        'Clear': 'Limpiar',
        'Font Size:': 'Tamaño de fuente:',
        'Pro Features': 'Funciones Pro',
        'Font Weight:': 'Grosor de fuente:',
        'GENERATE CONTEXT!': '¡GENERAR CONTEXTO!',
        'Select All': 'Seleccionar todo',
        'Deselect All': 'Deseleccionar todo',
        'Load preferences': 'Cargar preferencias',
        'Quit': 'Salir',
    },
    'zh_CN': {  # Chinese Simplified
        'aicodeprep-gui - File Selection': 'aicodeprep-gui - 文件选择',
        '&File': '文件(&F)',
        '&Quit': '退出(&Q)',
        '&Edit': '编辑(&E)',
        '&New Preset…': '新建预设(&N)…',
        'Open Settings Folder…': '打开设置文件夹…',
        '&Language / Idioma / 语言…': '语言 / Language / Idioma(&L)…',
        '&Flow': '流程(&F)',
        'Import Flow JSON…': '导入流程 JSON…',
        'Export Flow JSON…': '导出流程 JSON…',
        'Reset to Default Flow': '重置为默认流程',
        '&Help': '帮助(&H)',
        'Help / Links and Guides': '帮助 / 链接和指南',
        '&About': '关于(&A)',
        'Send Ideas, bugs, thoughts!': '发送想法、错误、想法！',
        'Activate Pro…': '激活专业版…',
        '&Debug': '调试(&D)',
        'Take Screenshot': '截图',
        'Current Language Info': '当前语言信息',
        'Accessibility Check': '辅助功能检查',
        '&Output format:': '输出格式(&O):',
        'Estimated tokens: 0': '估计令牌数: 0',
        'The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into your AI assistant.': '所选文件将与您的提示一起添加到 LLM 上下文块中，写入 fullcode.txt 并复制到剪贴板，准备粘贴到您的 AI 助手中。',
        'Prompt Preset Buttons:': '提示预设按钮:',
        'Clear': '清除',
        'Font Size:': '字体大小:',
        'Pro Features': '专业功能',
        'Font Weight:': '字体粗细:',
        'GENERATE CONTEXT!': '生成上下文！',
        'Select All': '全选',
        'Deselect All': '取消全选',
        'Load preferences': '加载首选项',
        'Quit': '退出',
    },
    'fr': {  # French
        'aicodeprep-gui - File Selection': 'aicodeprep-gui - Sélection de fichiers',
        '&File': '&Fichier',
        '&Quit': '&Quitter',
        '&Edit': '&Édition',
        '&New Preset…': '&Nouveau préréglage…',
        'Open Settings Folder…': 'Ouvrir le dossier des paramètres…',
        '&Language / Idioma / 语言…': '&Langue / Language / 语言…',
        '&Flow': '&Flux',
        'Import Flow JSON…': 'Importer JSON de flux…',
        'Export Flow JSON…': 'Exporter JSON de flux…',
        'Reset to Default Flow': 'Réinitialiser au flux par défaut',
        '&Help': '&Aide',
        'Help / Links and Guides': 'Aide / Liens et guides',
        '&About': 'À &propos',
        'Send Ideas, bugs, thoughts!': 'Envoyer des idées, bugs, réflexions !',
        'Activate Pro…': 'Activer Pro…',
        '&Debug': '&Déboguer',
        'Take Screenshot': 'Prendre une capture d\'écran',
        'Current Language Info': 'Informations sur la langue actuelle',
        'Accessibility Check': 'Vérification de l\'accessibilité',
        '&Output format:': '&Format de sortie :',
        'Estimated tokens: 0': 'Jetons estimés : 0',
        'The selected files will be added to the LLM Context Block along with your prompt, written to fullcode.txt and copied to clipboard, ready to paste into your AI assistant.': 'Les fichiers sélectionnés seront ajoutés au bloc de contexte LLM avec votre instruction, écrits dans fullcode.txt et copiés dans le presse-papiers, prêts à être collés dans votre assistant IA.',
        'Prompt Preset Buttons:': 'Boutons de préréglage :',
        'Clear': 'Effacer',
        'Font Size:': 'Taille de police :',
        'Pro Features': 'Fonctionnalités Pro',
        'Font Weight:': 'Graisse de police :',
        'GENERATE CONTEXT!': 'GÉNÉRER LE CONTEXTE !',
        'Select All': 'Tout sélectionner',
        'Deselect All': 'Tout désélectionner',
        'Load preferences': 'Charger les préférences',
        'Quit': 'Quitter',
    }
}


def add_translations_to_ts_file(ts_file_path: Path, lang_code: str):
    """Add translations to a .ts file."""
    print(f"\nProcessing {ts_file_path.name} ({lang_code})...")
    
    translations = TRANSLATIONS.get(lang_code, {})
    if not translations:
        print(f"  No translations defined for {lang_code}")
        return
    
    try:
        # Parse the XML
        tree = ET.parse(ts_file_path)
        root = tree.getroot()
        
        translated_count = 0
        
        # Find all message elements
        for message in root.findall('.//message'):
            source_elem = message.find('source')
            translation_elem = message.find('translation')
            
            if source_elem is not None and translation_elem is not None:
                source_text = source_elem.text
                
                # Check if we have a translation
                if source_text in translations:
                    # Update the translation
                    translation_elem.text = translations[source_text]
                    # Remove the 'type' attribute (marks as finished)
                    if 'type' in translation_elem.attrib:
                        del translation_elem.attrib['type']
                    translated_count += 1
        
        # Write back to file
        tree.write(ts_file_path, encoding='utf-8', xml_declaration=True)
        print(f"  ✓ Added {translated_count} translations")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    """Add translations to all .ts files."""
    project_root = Path(__file__).parent.parent
    trans_dir = project_root / "aicodeprep_gui" / "i18n" / "translations"
    
    # Add translations for each language
    for lang_code in ['es', 'zh_CN', 'fr']:
        ts_file = trans_dir / f"aicodeprep_gui_{lang_code}.ts"
        if ts_file.exists():
            add_translations_to_ts_file(ts_file, lang_code)
        else:
            print(f"Warning: {ts_file} not found")
    
    print("\n=== Translation addition complete ===")
    print("Run generate_translations.py to recompile .qm files")


if __name__ == "__main__":
    main()
