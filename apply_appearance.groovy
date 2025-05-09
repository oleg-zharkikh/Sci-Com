import org.gephi.project.api.ProjectController;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.appearance.api.AppearanceController;
import org.gephi.appearance.api.AttributeFunction;
import org.gephi.graph.api.GraphModel;
import org.openide.util.Lookup;

// Загрузка проекта и файла
def pc = Lookup.getDefault().lookup(ProjectController.class);
pc.newProject();
def importController = Lookup.getDefault().lookup(ImportController.class);
def container = importController.importFile(new File("graph_with_appearance.gexf"));
importController.process(container, new DefaultProcessor(), pc.getCurrentWorkspace());

// Настройка визуализации
def graphModel = pc.getCurrentWorkspace().getLookup().lookup(GraphModel.class);
def appearanceController = Lookup.getDefault().lookup(AppearanceController.class);

// Установка размеров узлов из атрибута "size"
def sizeAttr = graphModel.getNodeTable().getColumn("size");
if (sizeAttr != null) {
    def sizeFunction = appearanceController.getNodeAttributeFunction(sizeAttr);
    appearanceController.transform(sizeFunction);
}

// Установка цветов узлов из атрибута "color"
def colorAttr = graphModel.getNodeTable().getColumn("color");
if (colorAttr != null) {
    def colorFunction = appearanceController.getNodeAttributeFunction(colorAttr);
    appearanceController.transform(colorFunction);
}

// Сохранение проекта (опционально)
pc.saveProject(new File("output.gephi"));
