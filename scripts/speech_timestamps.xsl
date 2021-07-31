<?xml version="1.0"?>

<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Header row -->
    <xsl:template match="/">
        <xsl:text>id, word, start, start since, end, end since, speaker, role</xsl:text>
        <xsl:text>&#xA;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- Word row -->
    <xsl:template match="//tei:w">
        <!-- id, preceding anchor id, following anchor id variables -->
        <xsl:variable name="word_id" select="@xml:id"/>
        <xsl:variable name="word_start"><xsl:value-of select="$word_id"/>.ab</xsl:variable>
        <xsl:variable name="word_end"><xsl:value-of select="$word_id"/>.ae</xsl:variable>

        <!-- TODO 
            - preceding and following anchor audio id variables
            - variables will be acquired analogously to start since, end since 
        -->

        <!-- TODO 
            - possibly don't need to replace `start since` below; we might wish to
              to preserve the info about the audio origin
        -->

        <!-- id -->
        <xsl:value-of select="$word_id"/>
        <xsl:text>,</xsl:text>

        <!-- word -->
        <xsl:value-of select="."/>
        <xsl:text>,</xsl:text>

        <!-- TODO get rid of `start since`, replace by `start absolute` using 
            variables introduced above
        -->

        <!-- start -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_start]/@interval"/>
        <xsl:text>,</xsl:text>

        <!-- start since -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_start]/@since"/>
        <xsl:text>,</xsl:text>

        <!-- TODO get rid of `end since`, replace by `end absolute` using 
            variables introduced above
        -->

        <!-- end -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_end]/@interval"/>
        <xsl:text>,</xsl:text>

        <!-- end since -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_end]/@since"/>
        <xsl:text>,</xsl:text>

        <!-- speaker -->
        <xsl:value-of select="ancestor::tei:u/@who"/>
        <xsl:text>,</xsl:text>

        <!-- role -->
        <xsl:value-of select="ancestor::tei:u/@ana"/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>


    <!-- Remove everything else -->
    <xsl:template match="text()" />

</xsl:stylesheet> 

