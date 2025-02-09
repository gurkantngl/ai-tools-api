from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Matematik işlemleri için prompt template
MATH_PROMPT = """Sen bir matematik asistanısın. Sana verilen matematik işlemini çöz ve sadece sonucu döndür.
Lütfen sadece sayısal sonucu ver, başka açıklama yapma.

İşlem: {operation}

Sonuç:"""

class MathOperations:
    def __init__(self):
        # LLM modelini başlat
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Prompt template'i oluştur
        self.prompt = PromptTemplate(
            input_variables=["operation"],
            template=MATH_PROMPT
        )
        
        # LLM Chain'i oluştur
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt
        )
    
    async def solve_operation(self, operation: str) -> float:
        """
        Verilen matematik işlemini LLM kullanarak çözer.
        
        Args:
            operation (str): Çözülecek matematik işlemi (örn: "3 * 4 + 2")
            
        Returns:
            float: İşlemin sonucu
        """
        try:
            # LLM'den yanıt al
            response = await self.chain.ainvoke({"operation": operation})
            result = response['text'].strip()
            
            # Sonucu float'a çevir
            return float(result)
        except ValueError as e:
            raise ValueError(f"Sonuç sayısal bir değere dönüştürülemedi: {str(e)}")
        except Exception as e:
            raise Exception(f"İşlem çözülürken bir hata oluştu: {str(e)}")

class MathTool:
    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b 