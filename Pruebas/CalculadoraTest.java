import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CalculadoraTest {

    @BeforeEach
    void setUp() {
    }

    @AfterEach
    void tearDown() {
    }
    // Pruebas para el método sumar
    /**
     * Método prueba suma sumar enteros
     */
    @Test
    public void testSumar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(25.0, calculadora.sumar(20.0, 5.0));
    }

    @Test
    /**
     * Método prueba suma sumar negativos
     */
    public void testSumarNegativos() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-5.0, calculadora.sumar(-2.0, -3.0));
    }

    @Test
    /**
     * Método prueba suma sumar decimales
     */
    public void testSumarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.5, calculadora.sumar(2.3, 0.2));
    }
    // Pruebas para el método restar
    @Test
    /**
     * Método restar  restar enteros
     */
    public void testRestar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.0, calculadora.restar(8.0, 3.0));
    }

    @Test
    /**
     * Método restar  restar negativos
     */
    public void testRestarNegativos() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-5.0, calculadora.restar(-2.0, 3.0));
    }

    @Test
    /**
     * Método restar  restar decimales
     */
    public void testRestarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(6.0, calculadora.restar(6.3, 0.3));
    }
    // Pruebas para el método multiplicar
    @Test
    /**
     * Método multiplicar multiplicar numeros enteros
     */
    public void testMultiplicar() {
        Calculadora calculadora = new Calculadora();
        assertEquals(6.0, calculadora.multiplicar(2.0, 3.0));
    }

    @Test

    /**
     * Método multiplicar multiplicar numeros decimales
     */
    public void testMultiplicarDecimales() {
        Calculadora calculadora = new Calculadora();
        assertEquals(4.6, calculadora.multiplicar(2.0, 2.3));
    }

    @Test
    /**
     * Método multiplicar multiplicar numeros entero por negativo
     */
    public void testMultiplicarNegativoPorPositivo() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-6.0, calculadora.multiplicar(-2.0, 3.0));
    }
    // Pruebas para el método dividir
    @Test
    /**
     * Método dividir dividir numeros enteros
     */
    public void testDividir() {
        Calculadora calculadora = new Calculadora();
        assertEquals(2.0, calculadora.dividir(6.0, 3.0));
    }

    @Test
    /**
     * Método dividir dividir entre cero
     */
    public void testDividirPorCero() {
        Calculadora calculadora = new Calculadora();
        assertEquals(0.0, calculadora.dividir(6.0, 0.0));
    }

    @Test
    /**
     * Método dividir dividir negtivos entre positivos
     */
    public void testDividirNegativoPositivo() {
        Calculadora calculadora = new Calculadora();
        assertEquals(-1.0, calculadora.dividir(-6.0, 6.0));
    }
}