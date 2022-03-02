[CustomToV8]
interface Node {
    const unsigned short ELEMENT_NODE = 1;
    attribute Node parentNode;
    [TreatReturnedNullStringAs=Null] attribute DOMString nodeName;
    [Custom] Node appendChild(Node newChild);
    void addEventListener(DOMString type, EventListener listener, optional boolean useCapture);
};

