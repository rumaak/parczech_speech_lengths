<?xml version="1.0"?>

<!--
    This script extracts time related data about every word together with 
    basic info about speaker.
    
    The resulting file consists of header row followed by a single row
    for each spoken word. Columns are comma-separated.
-->

<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Header row -->
    <xsl:template match="/">
        <xsl:text>id, word, start, start absolute, start file, end, end absolute, end file, speaker, role</xsl:text>
        <xsl:text>&#xA;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- Word row -->
    <xsl:template match="//tei:w">
        <!-- id, preceding anchor, following anchor related variables -->
        <xsl:variable name="word_id" select="@xml:id"/>

        <xsl:variable name="word_start"><xsl:value-of select="$word_id"/>.ab</xsl:variable>
        <xsl:variable name="word_start_since_hash">
            <xsl:value-of select="following::tei:when[@xml:id=$word_start]/@since"/>
        </xsl:variable>
        <xsl:variable name="word_start_since" select="substring($word_start_since_hash,2)"/>

        <xsl:variable name="word_end"><xsl:value-of select="$word_id"/>.ae</xsl:variable>
        <xsl:variable name="word_end_since_hash">
            <xsl:value-of select="following::tei:when[@xml:id=$word_end]/@since"/>
        </xsl:variable>
        <xsl:variable name="word_end_since" select="substring($word_end_since_hash,2)"/>

        <!-- id -->
        <xsl:value-of select="$word_id"/>
        <xsl:text>,</xsl:text>

        <!-- word -->
        <xsl:value-of select="."/>
        <xsl:text>,</xsl:text>

        <!-- start -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_start]/@interval"/>
        <xsl:text>,</xsl:text>

        <!-- start absolute -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_start_since]/@absolute"/>
        <xsl:text>,</xsl:text>

        <!-- start audio file -->
        <xsl:value-of select="substring(following::tei:timeline[@origin=$word_start_since_hash]/@corresp,2)"/>
        <xsl:text>,</xsl:text>

        <!-- end -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_end]/@interval"/>
        <xsl:text>,</xsl:text>

        <!-- end absolute -->
        <xsl:value-of select="following::tei:when[@xml:id=$word_end_since]/@absolute"/>
        <xsl:text>,</xsl:text>

        <!-- end audio file -->
        <xsl:value-of select="substring(following::tei:timeline[@origin=$word_end_since_hash]/@corresp,2)"/>
        <xsl:text>,</xsl:text>

        <!-- speaker -->
        <xsl:value-of select="substring(ancestor::tei:u/@who,2)"/>
        <xsl:text>,</xsl:text>

        <!-- role -->
        <xsl:value-of select="substring(ancestor::tei:u/@ana,2)"/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>


    <!-- Remove everything else -->
    <xsl:template match="text()" />

</xsl:stylesheet> 

