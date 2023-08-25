import SupportingClasses.CodeSimilarization as CodeSimilarization
import SupportingClasses.TokenProcessing as TokenProcessing


def tokenizePythonString(stringinput):
    #Processing needed before tokenization
    processedString = CodeSimilarization.change_names(stringinput)
    processedString = TokenProcessing.processCodeString(processedString)
    return(processedString)

